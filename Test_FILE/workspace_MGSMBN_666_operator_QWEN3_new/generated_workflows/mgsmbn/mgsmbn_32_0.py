# Workflow ID: mgsmbn_32_0
# Benchmark: mgsmbn
# Data Indices: [73, 97]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # Step 1: Initial problem classification and decomposition
        classification = await self.generate(
            instruction="""Thoroughly analyze this Bengali math word problem and classify its type. Consider:
            - Is it a proportional reasoning problem (ratios, percentages, scaling)?
            - Is it a multi-entity tracking problem (multiple people/objects with different quantities)?
            - Is it a sequential operation problem (steps that build on each other)?
            - Is it a rate problem (distance/speed/time, unit prices)?
            - Is it a distribution or comparison problem?
            Also identify:
            - The main question being asked
            - All numerical values and their contextual meaning
            - Key relationships (e.g., "twice as many", "12 less than")
            - Any hidden steps or implicit operations
            - Units involved (টাকা, ঘণ্টা, জিনিস, etc.)
            Provide a structured classification that will guide subsequent solution strategies.""",
            context=""
        )

        # Step 2: Decompose into subproblems
        subproblems = await self.decompose(
            instruction="""Break down this problem into minimal, solvable subproblems. Each subproblem should:
            - Be independently solvable with the given information
            - Have clearly defined inputs and expected outputs
            - Specify any dependencies on other subproblems
            - Use abstract entity names (Entity A, Entity B) rather than problem-specific names
            - Include the mathematical operation required (add, multiply, compare, etc.)
            Return a list of subproblems with IDs, descriptions, and dependencies.""",
            context=classification
        )

        # Step 3: Parallel solution generation for each subproblem
        async def solve_subproblem(subproblem):
            sp_id = subproblem['id']
            sp_desc = subproblem['description']
            
            # Generate initial solution attempt
            solution_attempt = await self.generate(
                instruction=f"""Solve subproblem {sp_id}: {sp_desc}
                Based on the overall problem classification and decomposition:
                {classification}
                
                Steps to follow:
                1. Restate the subproblem in clear mathematical terms
                2. Identify required inputs and their sources
                3. Show the calculation step by step
                4. Provide the numerical result with appropriate units
                5. Explain how this result will be used in dependent subproblems""",
                context=""
            )
            
            # Validate and revise if necessary
            validation = await self.generate(
                instruction=f"""Critically validate the solution for subproblem {sp_id}:
                - Are the calculations mathematically correct?
                - Are units handled properly?
                - Does the solution align with the original problem constraints?
                - Are there any logical inconsistencies?
                If errors are found, explain them specifically. Otherwise, state 'VALID'.""",
                context=solution_attempt
            )
            
            if "VALID" not in validation.upper():
                solution_attempt = await self.revise(
                    instruction=f"""Revise the solution for subproblem {sp_id} based on this feedback:
                    {validation}
                    
                    Requirements:
                    - Fix all identified errors
                    - Maintain step-by-step clarity
                    - Ensure numerical accuracy
                    - Preserve unit consistency""",
                    context=solution_attempt
                )
            
            return solution_attempt

        # Solve subproblems in parallel
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp) for sp in subproblems]
        )

        # Step 4: Synthesize subproblem solutions into final answer
        synthesis = await self.ensemble(
            instruction="""Synthesize all subproblem solutions into a complete, coherent answer to the original question.
            Steps:
            1. Combine the results from all subproblems in logical order
            2. Show how each subproblem contributes to the final answer
            3. Perform any final calculations needed to reach the ultimate result
            4. Verify that the final answer satisfies all constraints from the original problem
            5. Present the final numerical answer clearly at the end, prefixed with 'FINAL ANSWER: '
            
            The final answer must be a single numerical value (integer or decimal) as required by the problem domain.""",
            contexts_list=subproblem_solutions
        )

        # Step 5: Extract and verify final answer
        final_answer = await self.generate(
            instruction="""Extract the final numerical answer from the synthesis. The answer should be:
            - A single number (integer or decimal)
            - Prefixed with 'FINAL ANSWER: ' in the synthesis
            - Mathematically consistent with all subproblem solutions
            - Valid in the real-world context (non-negative, appropriate magnitude, etc.)
            
            If multiple numbers are present, select the one that directly answers the original question.
            If no clear final answer is found, re-examine the synthesis and extract the most plausible numerical result.
            
            Return ONLY the numerical value, nothing else.""",
            context=synthesis
        )

        # Step 6: Final verification and cleanup
        verified_answer = await self.revise(
            instruction="""Verify that this final answer is correct and properly formatted:
            - Is it a single numerical value?
            - Does it match the expected type (integer/decimal) for this problem?
            - Is it consistent with the original problem's constraints?
            - Is it free of any text or units (pure number only)?
            
            If any issues are found, correct them. Otherwise, return the number unchanged.
            Return ONLY the numerical value, nothing else.""",
            context=final_answer
        )

        return verified_answer.strip()
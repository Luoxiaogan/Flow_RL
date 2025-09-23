# Workflow ID: limr_126_0
# Benchmark: limr
# Data Indices: [127, 8]

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
        import json

        # Step 1: Decompose the problem into mathematical subproblems
        decomposition = await self.decompose(
            instruction="""Break down this mathematical problem into its fundamental subproblems. For each subproblem:
            - Identify the mathematical domain (combinatorics, number theory, geometry, algebra, etc.)
            - Specify the key variables, constraints, and required operations
            - Note dependencies on other subproblems
            - Estimate the complexity (low/medium/high) and potential pitfalls
            Return a structured list where each subproblem has a clear, actionable description.""",
            context=""
        )

        # Step 2: Parallel exploration of subproblems
        subproblem_tasks = []
        for i, subproblem in enumerate(decomposition):
            task = self.generate(
                instruction=f"""Solve the following mathematical subproblem:
                {json.dumps(subproblem, indent=2)}
                
                Approach:
                - Use domain-specific techniques (combinatorial identities, modular arithmetic, geometric transformations, etc.)
                - Show all critical steps and justifications
                - Flag any assumptions or potential error points
                - Express the result in the most reduced form possible""",
                context=""
            )
            subproblem_tasks.append(task)
        
        subproblem_solutions = await asyncio.gather(*subproblem_tasks)

        # Step 3: Synthesize subproblem solutions
        synthesis = await self.ensemble(
            instruction="""Synthesize the following subproblem solutions into a unified answer:
            - Identify how results from each subproblem combine (addition, multiplication, modular reduction, etc.)
            - Resolve any inconsistencies in variables or constraints
            - Derive the final mathematical expression for the answer
            - If multiple synthesis paths exist, choose the most mathematically sound
            Output the complete derivation leading to the final answer.""",
            contexts_list=subproblem_solutions
        )

        # Step 4: Generate initial solution code for computational verification
        code_solution = await self.programmer(
            instruction="""Convert the following mathematical derivation into executable Python code:
            - Use only integer arithmetic to avoid floating-point errors
            - Apply modular arithmetic where appropriate (especially for large numbers)
            - Include assertions to verify intermediate results
            - The final output must be an integer between 0 and 999
            - If the problem involves combinatorics, use math.comb or equivalent
            - If the problem involves geometry, use coordinate transformations as needed""",
            context=synthesis,
            max_retries=3
        )

        # Step 5: Adversarial revision - assume the solution is wrong and find flaws
        critique = await self.revise(
            instruction="""Critically evaluate the following solution under the assumption that it contains at least one error:
            - Check for algebraic mistakes, misapplied theorems, or overlooked constraints
            - Verify combinatorial counts for over/under-counting
            - Ensure modular arithmetic is applied correctly
            - Confirm that the final answer is in [0,999]
            - If no errors are found, explicitly state "NO ERRORS FOUND"
            - If errors are found, provide the corrected solution with detailed justification""",
            context=f"Original Synthesis:\n{synthesis}\n\nCode Solution:\n{code_solution}"
        )

        # Step 6: Confidence assessment and potential strategy pivot
        confidence = await self.generate(
            instruction="""Assess the confidence level (1-10) in the current solution path:
            - 1-3: Fundamental flaws likely, need complete strategy change
            - 4-6: Significant doubts, consider alternative approaches
            - 7-10: High confidence, proceed with minor refinements
            If confidence is below 7, propose an alternative mathematical approach that could resolve the issues identified in the critique.
            If confidence is 7 or above, summarize the key verification steps that support the solution's validity.""",
            context=f"Critique:\n{critique}"
        )

        # Step 7: Final refinement and answer extraction
        final_answer = await self.revise(
            instruction="""Extract the final integer answer from the solution, ensuring:
            - The answer is an integer between 0 and 999
            - If derived from a larger number, correct modular reduction was applied
            - If derived from a fraction, it was simplified to an integer
            - If negative, it was adjusted via modular arithmetic to the [0,999] range
            - Present ONLY the three-digit integer answer (e.g., '042' for 42) with no additional text""",
            context=f"Confidence Assessment:\n{confidence}\n\nCurrent Best Solution:\n{critique if 'NO ERRORS FOUND' in critique else synthesis}"
        )

        return final_answer
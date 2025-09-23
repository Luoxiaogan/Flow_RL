# Workflow ID: limr_83_0
# Benchmark: limr
# Data Indices: [348, 312]

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

        # STEP 1: CLASSIFY PROBLEM AND IDENTIFY STRATEGIES
        classification = await self.generate(
            instruction="""Perform a deep classification of this mathematical problem:
            1. Identify the primary mathematical domain (geometry, number theory, algebra, combinatorics, trigonometry, etc.)
            2. List all applicable solution strategies and mathematical tools (e.g., modular arithmetic, coordinate geometry, trigonometric identities, generating functions)
            3. Note any constraints, boundary conditions, or special cases mentioned
            4. Predict potential pitfalls or non-obvious insights required
            5. Estimate the number of distinct solution approaches that could work
            Format your response as a structured analysis with clear section headings.""",
            context=""
        )

        # STEP 2: GENERATE MULTIPLE SOLUTION APPROACHES IN PARALLEL
        # Create 3 complementary perspectives: algebraic, geometric/visual, and computational
        approach_instructions = [
            """Develop a purely algebraic/formal solution approach:
            - Translate the problem into equations, identities, or formal relationships
            - Use symbolic manipulation and mathematical theorems
            - Avoid numerical computation until final steps
            - Document each logical step clearly""",
            
            """Develop a geometric/visual or combinatorial reasoning approach:
            - Use diagrams, spatial reasoning, or counting principles
            - Leverage symmetry, invariants, or transformational thinking
            - Consider edge cases and special configurations
            - Explain intuitive insights that guide the solution""",
            
            """Develop a computational/algorithmic approach:
            - Identify what can be calculated programmatically
            - Outline the algorithm or computational steps needed
            - Specify what inputs the programmer would need
            - Consider precision, iteration, or brute-force if applicable"""
        ]

        approaches = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in approach_instructions]
        )

        # STEP 3: SYNTHESIZE AND SELECT BEST PATH
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the three solution approaches into a unified strategy:
            - Identify points of consensus and contradiction
            - Determine which approach is most reliable or efficient
            - Combine complementary insights from multiple approaches
            - Produce a step-by-step solution plan that leverages the best of each
            - Flag any remaining uncertainties or risky assumptions
            Output a clear, ordered plan with numbered steps.""",
            contexts_list=approaches
        )

        # STEP 4: EXECUTE SOLUTION WITH ITERATIVE VALIDATION
        solution = None
        validation_feedback = ""
        max_iterations = 3
        
        for iteration in range(max_iterations):
            # Generate or revise solution
            if iteration == 0:
                solution = await self.generate(
                    instruction=f"""Execute the solution plan below with extreme precision:
                    {synthesized_strategy}
                    
                    Requirements:
                    - Show all intermediate steps and calculations
                    - Justify each mathematical operation
                    - Maintain exact precision (no approximations)
                    - Box the final answer at the end""",
                    context=synthesized_strategy
                )
            else:
                solution = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    Previous solution: {solution}
                    Validation feedback: {validation_feedback}
                    
                    - Correct any identified errors
                    - Strengthen weak justifications
                    - Add missing steps or clarifications
                    - Re-verify all calculations""",
                    context=solution
                )

            # Validate solution
            validation_feedback = await self.generate(
                instruction=f"""Critically validate the solution:
                - Check for logical consistency and mathematical correctness
                - Verify that all problem constraints are satisfied
                - Attempt to find counterexamples or edge cases
                - Confirm the answer format is a 3-digit integer (000-999)
                - If no errors, state 'VALIDATED'. Otherwise, list specific errors.
                
                Solution to validate:
                {solution}""",
                context=solution
            )

            if "VALIDATED" in validation_feedback.upper():
                break

        # STEP 5: EXTRACT AND FORMAT FINAL ANSWER
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from the solution below:
            - The answer must be an integer between 000 and 999
            - If less than 100, pad with leading zeros (e.g., 42 → 042)
            - Verify this answer satisfies all original problem constraints
            - Output ONLY the three-digit number, nothing else
            
            Solution:
            {solution}""",
            context=solution
        )

        # Clean and return final answer
        # Extract only digits and ensure 3-digit format
        digits = re.sub(r'\D', '', final_answer)
        if len(digits) > 3:
            digits = digits[-3:]  # Take last 3 digits if too long
        elif len(digits) < 3:
            digits = digits.zfill(3)  # Pad with leading zeros
        
        return digits
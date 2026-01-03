# Workflow ID: mbpp_46_0
# Benchmark: mbpp
# Data Indices: [56, 107]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Initial Analysis - Extract function name and requirements
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Extract the function name from the test cases.
            2. Identify the inputs, outputs, and transformations required.
            3. Note any specific constraints or edge cases mentioned.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple candidate solutions
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Generate a brute-force solution that addresses all requirements.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Generate an optimized solution leveraging Python's standard library.""",
                context=analysis
            )
        )

        # Step 3: Ensemble - Select the best candidate solution
        selected_solution = await self.ensemble(
            instruction="""Evaluate the candidate solutions:
            1. Check correctness based on the test cases.
            2. Prefer solutions with better readability and efficiency.
            3. Ensure the function name matches the test cases.
            Select the most promising solution.""",
            contexts_list=candidates
        )

        # Step 4: Validation and Refinement - Iterate until all test cases pass
        max_iterations = 3
        for _ in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the solution:
                1. Check if it passes all test cases.
                2. Identify any issues or missing edge cases.
                Provide detailed feedback.""",
                context=selected_solution
            )

            if "error" not in validation.lower():
                break  # Exit loop if solution is valid

            # Refine the solution based on feedback
            selected_solution = await self.revise(
                instruction=f"""Fix the following issues:
                {validation}
                Ensure the solution adheres to the original requirements.""",
                context=selected_solution
            )

        # Step 5: Final Output - Ensure proper formatting and completeness
        final_code = await self.revise(
            instruction="""Ensure the final code:
            1. Includes all necessary imports at the top.
            2. Maintains proper indentation (4 spaces).
            3. Is executable without modifications.
            Return the complete Python code block.""",
            context=selected_solution
        )

        return final_code
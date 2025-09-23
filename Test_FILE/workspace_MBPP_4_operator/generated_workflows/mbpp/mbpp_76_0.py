# Workflow ID: mbpp_76_0
# Benchmark: mbpp
# Data Indices: [259, 34]

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
        import re

        # Step 1: Extract function name and interpret task
        initial_analysis = await self.generate(
            instruction="""Extract the function name from the test cases and interpret the task:
            - Identify the function name from assert statements
            - Summarize the task requirements
            - Classify the problem type (e.g., list operations, string manipulation)
            - List any explicit constraints or requirements""",
            context=""
        )

        # Step 2: Parallel exploration of solution strategies
        brute_force_attempt = self.generate(
            instruction=f"""Generate a brute-force solution based on the task:
            {initial_analysis}
            - Focus on correctness over efficiency
            - Include all necessary imports
            - Ensure proper indentation and syntax""",
            context=initial_analysis
        )
        efficient_attempt = self.generate(
            instruction=f"""Generate an efficient solution using Python's standard library:
            {initial_analysis}
            - Leverage built-in functions or modules
            - Optimize for performance
            - Include all necessary imports
            - Ensure proper indentation and syntax""",
            context=initial_analysis
        )
        parallel_results = await asyncio.gather(brute_force_attempt, efficient_attempt)

        # Step 3: Synthesize and select the best solution
        selected_solution = await self.ensemble(
            instruction="""Evaluate the solutions and select the best one:
            - Consider code simplicity and readability
            - Ensure adherence to task requirements
            - Prioritize solutions that pass test cases""",
            contexts_list=parallel_results
        )

        # Step 4: Validate and refine the solution
        max_iterations = 3
        for i in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                {selected_solution}
                - Check if all test cases pass
                - Identify any issues or errors""",
                context=selected_solution
            )
            if "error" in validation.lower() or "fail" in validation.lower():
                selected_solution = await self.revise(
                    instruction=f"""Fix issues identified during validation:
                    {validation}
                    - Correct syntax or logic errors
                    - Address any missing edge cases
                    - Ensure proper indentation and formatting""",
                    context=selected_solution
                )
            else:
                break

        # Step 5: Finalize the output
        final_code = await self.summarize(
            instruction="""Clean up the code and ensure it meets the required format:
            - Include all necessary imports at the top
            - Use 4-space indentation
            - Ensure the function name matches the test cases
            - Remove any redundant comments or code""",
            context=selected_solution
        )

        return final_code
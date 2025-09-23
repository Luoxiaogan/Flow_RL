# Workflow ID: mbpp_81_0
# Benchmark: mbpp
# Data Indices: [216, 181]

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

        # Step 1: Analyze the problem and extract key components
        analysis = await self.generate(
            instruction="""Analyze the problem and extract key components:
            - Task type (e.g., list operations, math computations, string manipulations)
            - Inputs, outputs, and constraints
            - Keywords or patterns indicating the solution approach
            - Potential edge cases""",
            context=""
        )

        # Step 2: Extract the function name from the test cases
        function_name = await self.generate(
            instruction="""Extract the function name from the test cases:
            - Identify the function name used in the assert statements
            - Ensure the extracted name matches the expected format""",
            context=analysis
        )
        function_name = re.search(r"(\w+)\(", function_name).group(1)  # Extract the name using regex

        # Step 3: Generate multiple solution attempts in parallel
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using standard library functions:
                - Use the extracted function name: {function_name}
                - Translate the problem description into Python logic
                - Include necessary imports and ensure proper syntax""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using custom logic:
                - Use the extracted function name: {function_name}
                - Focus on implementing the logic manually without relying on built-in functions
                - Ensure the solution is complete and executable""",
                context=analysis
            )
        )

        # Step 4: Select the best solution using ensemble
        best_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Evaluate completeness, correctness, and readability
            - Prefer solutions that use standard library functions unless custom logic is more appropriate""",
            contexts_list=solutions
        )

        # Step 5: Validate and refine the solution iteratively
        max_iterations = 3
        for i in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                - Check if the code passes all assertions
                - Identify any errors or missing details
                - Provide feedback for refinement""",
                context=best_solution
            )
            if "error" in validation.lower():
                best_solution = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback:
                    - Address identified issues
                    - Improve clarity and correctness
                    - Ensure the code remains aligned with the test cases""",
                    context=best_solution
                )
            else:
                break

        # Step 6: Finalize and return the solution
        finalized_code = await self.revise(
            instruction="""Finalize the solution:
            - Ensure proper indentation and syntax
            - Include all necessary imports
            - Verify alignment with the function name and test cases""",
            context=best_solution
        )
        return finalized_code
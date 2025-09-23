# Workflow ID: mbpp_38_0
# Benchmark: mbpp
# Data Indices: [351, 358]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem description:
            - Identify the function name from assert statements.
            - Classify the problem type (e.g., mathematical, list manipulation).
            - Extract key inputs and outputs.
            - Highlight any ambiguities or missing details.""",
            context=""
        )

        # Extract function name using regex
        function_name_match = re.search(r'assert\s+(\w+)\(', self.problem_text)
        function_name = function_name_match.group(1) if function_name_match else "unknown_function"

        # Step 2: Parallel Solution Generation
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct implementation of the function '{function_name}'.
                - Use basic Python constructs.
                - Ensure the function matches the test cases.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate an implementation using Python's standard library for '{function_name}'.
                - Leverage built-in functions and modules.
                - Optimize for clarity and efficiency.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a recursive implementation of '{function_name}' if applicable.
                - Handle base cases and recursive steps.
                - Ensure termination conditions are clear.""",
                context=analysis
            )
        )

        # Step 3: Ensemble Selection
        selected_solution = await self.ensemble(
            instruction=f"""Select the best implementation for '{function_name}':
            - Prefer simplicity and correctness.
            - Ensure adherence to test cases.
            - Avoid unnecessary complexity.""",
            contexts_list=candidates
        )

        # Step 4: Validation and Refinement
        max_iterations = 5
        for iteration in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the solution for '{function_name}' against the test cases:
                - Check syntax and structure.
                - Ensure all test cases pass.
                - Identify any errors or edge cases.""",
                context=selected_solution
            )

            if "error" not in validation.lower():
                break  # Exit loop if no errors

            selected_solution = await self.revise(
                instruction=f"""Refine the solution for '{function_name}':
                - Fix identified issues.
                - Improve clarity and robustness.
                - Handle edge cases if necessary.""",
                context=selected_solution
            )

        # Step 5: Final Output
        final_code = await self.generate(
            instruction=f"""Format the final solution for '{function_name}':
            - Include all necessary imports.
            - Ensure proper indentation and structure.
            - Match the function name and parameters from test cases.""",
            context=selected_solution
        )

        return final_code
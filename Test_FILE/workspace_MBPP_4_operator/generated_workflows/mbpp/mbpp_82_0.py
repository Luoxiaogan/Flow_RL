# Workflow ID: mbpp_82_0
# Benchmark: mbpp
# Data Indices: [339]

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

        # Step 1: Extract function name and validate
        function_name_context = await self.generate(
            instruction="""Extract the function name from the assert statements.
            Ensure that the name appears consistently across all test cases.
            Format the response as: 'Function Name: <name>'""",
            context=""
        )
        function_name = re.search(r'Function Name: (\w+)', function_name_context).group(1)

        # Step 2: Decompose task and identify requirements
        task_summary = await self.generate(
            instruction=f"""Analyze the task description and test cases.
            Identify:
            - Input types (e.g., list, integer, string)
            - Expected output types
            - Key operations (e.g., sorting, filtering, mathematical computation)
            - Any edge cases implied by the test cases
            Function Name: {function_name}""",
            context=""
        )

        # Step 3: Generate candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Implement the solution using a custom algorithm.
                Focus on clarity and correctness.
                Function Name: {function_name}
                Task Summary: {task_summary}""",
                context=""
            ),
            self.generate(
                instruction=f"""Implement the solution using Python's standard library.
                Leverage built-in functions and modules where applicable.
                Function Name: {function_name}
                Task Summary: {task_summary}""",
                context=""
            ),
            self.generate(
                instruction=f"""Implement the solution using a hybrid approach.
                Combine custom logic with standard library functions.
                Function Name: {function_name}
                Task Summary: {task_summary}""",
                context=""
            )
        )

        # Step 4: Select the best solution using ensemble
        selected_solution = await self.ensemble(
            instruction=f"""Evaluate the following candidate solutions:
            1. Custom Algorithm: {candidates[0]}
            2. Standard Library: {candidates[1]}
            3. Hybrid Approach: {candidates[2]}
            
            Select the solution that:
            - Passes all test cases
            - Handles edge cases correctly
            - Is efficient and maintainable
            Provide the selected solution.""",
            contexts_list=candidates
        )

        # Step 5: Validate and refine the selected solution
        final_code = await self.revise(
            instruction=f"""Ensure that the following code passes all test cases:
            - Correctly implements the function '{function_name}'
            - Handles all edge cases
            - Follows Pythonic conventions
            Refine the code if necessary.
            Selected Solution: {selected_solution}""",
            context=selected_solution
        )

        return final_code
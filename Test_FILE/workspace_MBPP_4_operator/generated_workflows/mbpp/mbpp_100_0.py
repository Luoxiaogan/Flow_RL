# Workflow ID: mbpp_100_0
# Benchmark: mbpp
# Data Indices: [18, 258]

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

        # Step 1: Extract function name and input types from test cases
        function_info = await self.generate(
            instruction="""Extract the function name and input types from the test cases:
            - Identify the function name used in assert statements
            - Determine the number and types of arguments
            - Provide the extracted information in a structured format""",
            context=""
        )

        # Step 2: Analyze the task description
        task_analysis = await self.generate(
            instruction="""Analyze the task description:
            - Identify the problem type (e.g., list operations, string manipulation)
            - List all requirements explicitly stated in the description
            - Infer any implicit requirements or constraints
            - Highlight potential edge cases""",
            context=""
        )

        # Step 3: Generate multiple candidate solutions
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on list/array operations:
                Function Info: {function_info}
                Task Analysis: {task_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on string manipulation:
                Function Info: {function_info}
                Task Analysis: {task_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on mathematical computations:
                Function Info: {function_info}
                Task Analysis: {task_analysis}""",
                context=""
            )
        )

        # Step 4: Select the best solution
        best_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Clarity and readability of the code
            - Alignment with the task description and test cases
            - Robustness in handling edge cases""",
            contexts_list=candidates
        )

        # Step 5: Refine the selected solution
        refined_code = await self.revise(
            instruction="""Refine the generated code:
            - Ensure proper indentation and syntax
            - Add necessary imports at the top of the code
            - Handle edge cases explicitly
            - Improve clarity and readability""",
            context=best_solution
        )

        # Step 6: Validate the refined code
        validation_result = await self.generate(
            instruction=f"""Validate the refined code against the test cases:
            Refined Code: {refined_code}
            Test Cases: {re.findall(r'assert.*', self.problem_text)}""",
            context=""
        )

        # Step 7: Iterate if validation fails
        while "fail" in validation_result.lower():
            refined_code = await self.revise(
                instruction=f"""Fix issues identified during validation:
                Validation Result: {validation_result}
                Current Code: {refined_code}""",
                context=refined_code
            )
            validation_result = await self.generate(
                instruction=f"""Re-validate the fixed code:
                Fixed Code: {refined_code}
                Test Cases: {re.findall(r'assert.*', self.problem_text)}""",
                context=""
            )

        # Step 8: Format and return the final code
        final_code = f"
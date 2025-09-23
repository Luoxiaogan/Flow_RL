# Workflow ID: mbpp_48_0
# Benchmark: mbpp
# Data Indices: [248]

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

        # Step 1: Extract function name and test cases
        function_info = await self.generate(
            instruction="""Extract the function name and test cases from the problem text.
            Format the output as:
            Function Name: <name>
            Test Cases:
            - Input: <input>, Expected Output: <output>
            - Input: <input>, Expected Output: <output>""",
            context=""
        )

        # Parse function name and test cases
        function_name_match = re.search(r"Function Name: (\w+)", function_info)
        function_name = function_name_match.group(1) if function_name_match else "solution"
        test_cases = re.findall(r"- Input: (.+?), Expected Output: (.+)", function_info)

        # Step 2: Analyze task description
        task_analysis = await self.generate(
            instruction=f"""Analyze the task description to identify:
            - Core operation (e.g., summing, filtering, transforming)
            - Input constraints (e.g., integers, lists, strings)
            - Output format (e.g., single value, list, dictionary)
            Problem Text: {self.problem_text}""",
            context=""
        )

        # Step 3: Generate candidate solutions
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct implementation of the core operation.
                Task Analysis: {task_analysis}
                Function Name: {function_name}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an alternative implementation using a different approach.
                Task Analysis: {task_analysis}
                Function Name: {function_name}""",
                context=""
            )
        )

        # Step 4: Validate and refine solutions
        refined_solutions = []
        for candidate in candidates:
            validation = await self.revise(
                instruction=f"""Validate the solution against the test cases.
                Test Cases: {test_cases}
                Solution: {candidate}""",
                context=candidate
            )
            if "error" not in validation.lower():
                refined_solutions.append(candidate)
            else:
                refined = await self.revise(
                    instruction=f"""Refine the solution to fix identified issues.
                    Issues: {validation}
                    Solution: {candidate}""",
                    context=candidate
                )
                refined_solutions.append(refined)

        # Step 5: Ensemble selection
        best_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Passing all test cases
            - Code clarity and maintainability
            - Computational efficiency""",
            contexts_list=refined_solutions
        )

        # Step 6: Finalize code
        final_code = await self.revise(
            instruction=f"""Ensure the solution includes all necessary imports and adheres to formatting requirements.
            Solution: {best_solution}""",
            context=best_solution
        )

        return final_code
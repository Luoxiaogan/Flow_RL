# Workflow ID: mbpp_113_0
# Benchmark: mbpp
# Data Indices: [112]

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
        """
        Universal workflow for code generation from natural language descriptions.
        """
        import asyncio
        import re

        # Step 1: Extract key components from the task description
        task_analysis = await self.generate(
            instruction="""Analyze the problem description to identify:
            - Input types and structures
            - Expected output format
            - Special conditions or constraints
            - Problem category (e.g., list operations, math, string manipulation)""",
            context=""
        )
        refined_task = await self.revise(
            instruction="Clarify ambiguities and ensure completeness.",
            context=task_analysis
        )

        # Step 2: Extract function name and signature from test cases
        func_extraction = await self.generate(
            instruction="""Extract the function name and its signature from the test cases.
            Ensure the function name matches exactly what appears in the assertions.""",
            context=refined_task
        )
        func_name_match = re.search(r"def (\w+)\(", func_extraction)
        func_name = func_name_match.group(1) if func_name_match else "unknown_function"

        # Step 3: Generate initial code solution
        code_generation = await self.generate(
            instruction=f"""Generate Python code for the function `{func_name}`.
            - Include all necessary imports
            - Use proper indentation (4 spaces)
            - Handle edge cases mentioned in the task analysis
            - Ensure the code passes the provided test cases""",
            context=refined_task
        )

        # Step 4: Refine the generated code
        refined_code = await self.revise(
            instruction="""Improve clarity, add missing details, and ensure the code adheres to Python best practices.
            - Validate against edge cases
            - Ensure proper error handling
            - Optimize for readability and efficiency""",
            context=code_generation
        )

        # Step 5: Validate the solution against test cases
        validation = await self.generate(
            instruction=f"""Validate the generated code `{func_name}` against the provided test cases.
            - Check if all assertions pass
            - Identify any discrepancies or errors""",
            context=refined_code
        )
        final_code = await self.ensemble(
            instruction="Ensure the final code is robust, correct, and adheres to all requirements.",
            contexts_list=[refined_code, validation]
        )

        return final_code
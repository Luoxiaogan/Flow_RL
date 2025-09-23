# Workflow ID: mbpp_61_0
# Benchmark: mbpp
# Data Indices: [99]

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

        # Step 1: Extract function name and analyze task
        function_name = await self.generate(
            instruction="""Extract the function name from the assert statements.
            Ensure the name matches exactly as it appears in the test cases.
            Provide only the function name without additional text.""",
            context=""
        )
        function_name = function_name.strip()

        task_analysis = await self.generate(
            instruction="""Analyze the task description to determine:
            - The type of problem (e.g., list operations, mathematical computations)
            - Required inputs and outputs
            - Any specific constraints or requirements""",
            context=""
        )

        # Step 2: Parallel exploration of interpretations
        interpretations = await asyncio.gather(
            self.generate(
                instruction="Interpret the task focusing on logical reasoning.",
                context=task_analysis
            ),
            self.generate(
                instruction="Interpret the task focusing on mathematical computations.",
                context=task_analysis
            ),
            self.generate(
                instruction="Interpret the task focusing on data structure manipulations.",
                context=task_analysis
            )
        )

        # Step 3: Synthesize the most accurate interpretation
        synthesized_interpretation = await self.ensemble(
            instruction="Combine insights from all interpretations into a unified understanding.",
            contexts_list=interpretations
        )

        # Step 4: Generate initial Python code
        code_attempt = await self.generate(
            instruction=f"""Generate Python code based on the following:
            Function Name: {function_name}
            Task Interpretation: {synthesized_interpretation}
            Include necessary imports at the top of the code.
            Ensure proper indentation and formatting.""",
            context=""
        )

        # Step 5: Validate and refine the code
        max_attempts = 5
        for attempt in range(max_attempts):
            validation_result = await self.generate(
                instruction=f"""Test the following code against the provided assertions:
                Code:
                {code_attempt}
                Identify any errors or mismatches with the test cases.""",
                context=""
            )

            if "error" not in validation_result.lower():
                break  # Code passes all test cases

            # Refine the code based on validation feedback
            code_attempt = await self.revise(
                instruction=f"""Fix the following issues in the code:
                Issues: {validation_result}
                Original Code:
                {code_attempt}""",
                context=code_attempt
            )

        return code_attempt
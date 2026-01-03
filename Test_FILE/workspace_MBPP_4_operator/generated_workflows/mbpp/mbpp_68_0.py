# Workflow ID: mbpp_68_0
# Benchmark: mbpp
# Data Indices: [323, 23]

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

        # Step 1: Extract function name and input types from test cases
        extraction_tasks = await asyncio.gather(
            self.summarize(
                instruction="Extract the function name from the assert statements. "
                            "Provide only the function name without additional explanation.",
                context=""
            ),
            self.summarize(
                instruction="Identify the input types and expected output type from the assert statements. "
                            "Format the response as 'input1_type, input2_type -> output_type'.",
                context=""
            )
        )
        function_name = extraction_tasks[0].strip()
        signature = extraction_tasks[1].strip()

        # Step 2: Understand the task from the natural language description
        task_understanding = await self.generate(
            instruction=f"Based on the natural language description, explain the task requirements. "
                        f"Include details about what the function should do and any edge cases to consider.",
            context=""
        )

        # Step 3: Generate initial code
        initial_code = await self.generate(
            instruction=f"Write a Python function named '{function_name}' with the signature '{signature}'. "
                        f"The function should satisfy the following requirements: {task_understanding}. "
                        f"Ensure proper indentation and include all necessary imports.",
            context=""
        )

        # Step 4: Validate and refine the code
        max_attempts = 3
        for attempt in range(max_attempts):
            validation = await self.generate(
                instruction=f"Test the following code against the provided test cases:\n{initial_code}\n"
                            f"If the code fails any test case, explain why it failed and suggest improvements.",
                context=""
            )
            if "fail" not in validation.lower():
                break  # Code passes all test cases
            initial_code = await self.revise(
                instruction=f"Refine the following code based on the validation feedback:\n{validation}",
                context=initial_code
            )

        # Step 5: Return the final code
        return initial_code
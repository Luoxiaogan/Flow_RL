# Workflow ID: mbpp_40_0
# Benchmark: mbpp
# Data Indices: [199]

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

        # Step 1: Parallel Fork - Extract function name and parse requirements
        function_name_task = self.generate(
            instruction="Extract the function name from the assert statements. "
                        "Ensure the function name is accurate and matches the test cases.",
            context=""
        )
        requirements_task = self.generate(
            instruction="Analyze the task description to understand the requirements. "
                        "Identify the input, output, and any specific logic needed.",
            context=""
        )

        function_name, requirements = await asyncio.gather(function_name_task, requirements_task)

        # Step 2: Merge - Generate initial code attempt
        initial_code = await self.generate(
            instruction=f"Generate Python code for the function '{function_name}'. "
                        f"Requirements: {requirements}. Ensure all necessary imports are included.",
            context=""
        )

        # Step 3: Iterative Loop - Validate and refine code
        max_iterations = 5
        for iteration in range(max_iterations):
            validation_result = await self.generate(
                instruction=f"Validate the following code against the provided test cases:\n{initial_code}\n"
                            f"Identify any errors or mismatches.",
                context=initial_code
            )

            if "error" not in validation_result.lower():
                break  # Code passes all test cases

            # Refine the code based on validation feedback
            initial_code = await self.revise(
                instruction=f"Fix the following issues in the code:\n{validation_result}\n"
                            f"Ensure the code passes all test cases.",
                context=initial_code
            )

        return initial_code
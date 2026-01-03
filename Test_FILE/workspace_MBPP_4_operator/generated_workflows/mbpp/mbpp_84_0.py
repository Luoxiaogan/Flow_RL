# Workflow ID: mbpp_84_0
# Benchmark: mbpp
# Data Indices: [245, 159]

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

        # Step 1: Extract function name and requirements
        function_info = await self.generate(
            instruction="""Extract the function name and its parameters from the test cases.
            Analyze the natural language description to understand the problem requirements.
            Provide the function signature and a brief summary of the task.""",
            context=""
        )

        # Step 2: Generate initial code
        initial_code = await self.generate(
            instruction=f"""Based on the following function information:
            {function_info}
            
            Generate the initial Python code implementation.
            Ensure the function name and parameters match the test cases.
            Include necessary imports at the top of the code.""",
            context=function_info
        )

        # Step 3: Validate and refine
        validation_results = []
        max_attempts = 3
        for attempt in range(max_attempts):
            validation_result = await self.generate(
                instruction=f"""Validate the following code against the provided test cases:
                {initial_code}
                
                Identify any failing test cases and explain why they fail.""",
                context=initial_code
            )
            validation_results.append(validation_result)

            if "pass" in validation_result.lower():
                break

            # Refine the code based on validation results
            initial_code = await self.revise(
                instruction=f"""Refine the following code based on the validation results:
                Validation Results: {validation_result}
                
                Correct the errors and improve the implementation.""",
                context=initial_code
            )

        # Step 4: Handle edge cases
        edge_cases = await self.generate(
            instruction=f"""Analyze the test cases to identify potential edge cases:
            {initial_code}
            
            Generate additional test cases to cover these scenarios.""",
            context=initial_code
        )

        # Step 5: Finalize the code
        finalized_code = await self.revise(
            instruction=f"""Finalize the following code:
            {initial_code}
            
            Ensure it includes all necessary imports, adheres to proper formatting, and is ready for execution.""",
            context=initial_code
        )

        return finalized_code
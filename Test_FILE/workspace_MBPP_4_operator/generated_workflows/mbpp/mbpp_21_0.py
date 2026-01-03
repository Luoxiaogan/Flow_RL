# Workflow ID: mbpp_21_0
# Benchmark: mbpp
# Data Indices: [171, 207]

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

        # Step 1: Initial Analysis (Parallel)
        function_signature_task = self.generate(
            instruction="Extract the function name and parameters from the test cases. "
                        "Provide the result in the format 'function_name(param1, param2, ...)'.",
            context=""
        )
        task_interpretation_task = self.generate(
            instruction="Interpret the natural language task description. "
                        "Provide a structured explanation of the requirements, including inputs, outputs, and logic.",
            context=""
        )
        function_signature, task_interpretation = await asyncio.gather(function_signature_task, task_interpretation_task)

        # Step 2: Code Generation
        code_attempt = await self.generate(
            instruction=f"Generate Python code for the function '{function_signature}' "
                        f"based on the following task interpretation:\n{task_interpretation}\n"
                        "Ensure proper indentation, include all necessary imports, and adhere to Python conventions.",
            context=""
        )

        # Step 3: Validation and Refinement (Iterative)
        MAX_ITERATIONS = 3
        for iteration in range(MAX_ITERATIONS):
            validation_result = await self.revise(
                instruction="Validate the generated code against the test cases. "
                            "If it fails, explain the failure mode (e.g., incorrect output, syntax error).",
                context=code_attempt
            )
            if "error" not in validation_result.lower():
                break  # Code passes validation
            code_attempt = await self.revise(
                instruction=f"Refine the code based on the following feedback:\n{validation_result}",
                context=code_attempt
            )

        # Step 4: Edge Case Handling
        edge_cases = await self.generate(
            instruction="Identify potential edge cases for the function based on the task description and test cases. "
                        "Provide examples and explain how the function should handle them.",
            context=""
        )
        final_code = await self.revise(
            instruction=f"Incorporate the following edge cases into the code:\n{edge_cases}",
            context=code_attempt
        )

        # Step 5: Final Synthesis
        synthesized_code = await self.ensemble(
            instruction="Synthesize the refined code into a final, polished version. "
                        "Ensure it is complete, executable, and adheres to all requirements.",
            contexts_list=[final_code, edge_cases]
        )

        return synthesized_code
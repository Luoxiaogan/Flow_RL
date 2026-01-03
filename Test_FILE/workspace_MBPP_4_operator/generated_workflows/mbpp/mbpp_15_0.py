# Workflow ID: mbpp_15_0
# Benchmark: mbpp
# Data Indices: [363]

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

        # Initial Analysis
        analysis_task = await self.generate(
            instruction="""Analyze the problem:
            - Extract the function name from assert statements
            - Identify input parameters and expected outputs
            - Summarize the task description and requirements""",
            context=""
        )

        # Function Name Validation
        function_name = await self.generate(
            instruction="""Extract the function name from the test cases:
            - Ensure it matches the format in assert statements
            - Validate against the problem description""",
            context=analysis_task
        )
        validated_function_name = await self.revise(
            instruction="Validate and refine the extracted function name",
            context=function_name
        )

        # Code Generation
        initial_code = await self.generate(
            instruction=f"""Generate Python code for the function:
            - Function name: {validated_function_name}
            - Inputs and outputs based on analysis
            - Include necessary imports and logic""",
            context=analysis_task
        )

        # Validation and Refinement Loop
        refined_code = initial_code
        for _ in range(3):  # Up to 3 refinement iterations
            validation = await self.revise(
                instruction="Validate the code against test cases and requirements",
                context=refined_code
            )
            if "error" not in validation.lower():
                break
            refined_code = await self.revise(
                instruction=f"Refine the code based on validation feedback: {validation}",
                context=refined_code
            )

        # Edge Case Exploration
        edge_cases = await self.generate(
            instruction="Identify potential edge cases and ensure the code handles them",
            context=refined_code
        )
        final_code = await self.revise(
            instruction=f"Incorporate edge case handling: {edge_cases}",
            context=refined_code
        )

        # Final Synthesis
        final_solution = await self.ensemble(
            instruction="Synthesize the final solution from all iterations",
            contexts_list=[initial_code, refined_code, final_code]
        )

        return final_solution
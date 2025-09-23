# Workflow ID: mbpp_119_0
# Benchmark: mbpp
# Data Indices: [235, 365]

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
        import json

        # Step 1: Analyze the problem
        analysis = await self.generate(
            instruction="Extract the function name, input types, output types, and task description. Format as a JSON object.",
            context=""
        )
        analysis_data = json.loads(analysis)

        # Step 2: Generate multiple candidate solutions
        candidates = await asyncio.gather(
            self.generate(instruction="Implement a direct solution based on the task description.", context=analysis),
            self.generate(instruction="Use mathematical reasoning to solve the problem.", context=analysis),
            self.generate(instruction="Leverage Python's standard library to implement the solution.", context=analysis)
        )

        # Step 3: Select the best solution
        best_solution = await self.ensemble(
            instruction="Select the best solution based on correctness, simplicity, and efficiency.",
            contexts_list=candidates
        )

        # Step 4: Refine the selected solution
        refined_code = await self.revise(
            instruction="Improve clarity, add necessary imports, and ensure proper indentation.",
            context=best_solution
        )

        # Step 5: Validate the refined code
        validation_result = await self.generate(
            instruction=f"Validate the following code against the test cases:\n{refined_code}",
            context=analysis
        )

        if "error" in validation_result.lower():
            # Iterate: Revise and revalidate
            final_code = await self.revise(
                instruction=f"Fix issues: {validation_result}",
                context=refined_code
            )
        else:
            final_code = refined_code

        return final_code
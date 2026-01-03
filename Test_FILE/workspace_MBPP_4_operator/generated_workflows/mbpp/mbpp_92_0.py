# Workflow ID: mbpp_92_0
# Benchmark: mbpp
# Data Indices: [335, 296]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract the function name and input/output patterns from the assert statements. 
            Analyze the task description to identify key components and classify the problem type (e.g., list operations, string manipulation).""",
            context=""
        )

        # Step 2: Parallel Exploration
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"Interpret the task as a sorting operation: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Interpret the task as a filtering operation: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Interpret the task as a mapping/transformation operation: {analysis}",
                context=analysis
            )
        )

        # Step 3: Ensemble Selection
        selected_solution = await self.ensemble(
            instruction="Select the most promising solution based on clarity, simplicity, and alignment with test cases.",
            contexts_list=candidates
        )

        # Step 4: Solution Generation
        initial_code = await self.generate(
            instruction=f"Generate Python code for the selected solution: {selected_solution}. "
                        f"Ensure proper imports, indentation, and adherence to Python conventions.",
            context=selected_solution
        )

        # Step 5: Validation and Refinement
        validation = await self.generate(
            instruction=f"Validate the solution against the provided test cases: {initial_code}",
            context=initial_code
        )
        if "error" in validation.lower():
            refined_code = await self.revise(
                instruction=f"Fix issues identified during validation: {validation}",
                context=initial_code
            )
        else:
            refined_code = initial_code

        # Step 6: Final Output
        final_output = f"
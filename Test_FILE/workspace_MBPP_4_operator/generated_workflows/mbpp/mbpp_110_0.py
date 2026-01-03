# Workflow ID: mbpp_110_0
# Benchmark: mbpp
# Data Indices: [249, 75]

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
            instruction="""Extract the function name from the test cases and parse the task description.
            - Identify the function name used in the assert statements.
            - Summarize the task requirements in structured form.
            - Highlight any ambiguities or missing details.""",
            context=""
        )

        # Step 2: Parallel Exploration
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using regex:
                - Function name: Extracted from analysis.
                - Requirements: {analysis}
                - Include necessary imports.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution without regex:
                - Function name: Extracted from analysis.
                - Requirements: {analysis}
                - Use standard string operations.""",
                context=analysis
            )
        )

        # Step 3: Validation and Selection
        selected_solution = await self.ensemble(
            instruction="Evaluate solutions against test cases. Select the one that passes all test cases or has the fewest errors.",
            contexts_list=solutions
        )

        # Step 4: Refinement Loop
        max_iterations = 3
        for i in range(max_iterations):
            validation = await self.generate(
                instruction=f"Validate the selected solution against test cases. Identify any errors or edge cases.",
                context=selected_solution
            )
            if "error" not in validation.lower():
                break
            selected_solution = await self.revise(
                instruction=f"Refine the solution based on validation feedback: {validation}",
                context=selected_solution
            )

        return selected_solution
# Workflow ID: mbpp_108_0
# Benchmark: mbpp
# Data Indices: [195, 96]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract the following information:
            - Function name from assert statements.
            - Input types and expected outputs from test cases.
            - Key requirements from the task description.
            Format the output as a structured summary.""",
            context=""
        )

        # Step 2: Solution Generation
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct implementation based on:
                {analysis}
                Use basic Python constructs without optimizations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate an optimized implementation using Python's standard library:
                {analysis}
                Focus on efficiency and readability.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a robust implementation that handles edge cases:
                {analysis}
                Consider empty inputs, invalid data, and large datasets.""",
                context=analysis
            )
        )

        # Step 3: Solution Evaluation
        evaluations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Evaluate the solution:
                - Check correctness against test cases.
                - Assess readability and efficiency.
                - Identify any edge case failures.
                Solution:
                {candidate}""",
                context=analysis
            ) for candidate in candidates]
        )
        best_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Correctness (passes all test cases).
            - Readability and maintainability.
            - Robustness in handling edge cases.""",
            contexts_list=evaluations
        )

        # Step 4: Iterative Refinement
        max_iterations = 3
        for _ in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the solution:
                - Does it pass all test cases?
                - Are there any logical or syntactic errors?
                Solution:
                {best_solution}""",
                context=analysis
            )
            if "error" in validation.lower():
                best_solution = await self.revise(
                    instruction=f"""Fix issues identified in the solution:
                    Issues:
                    {validation}
                    Solution:
                    {best_solution}""",
                    context=best_solution
                )
            else:
                break

        return best_solution
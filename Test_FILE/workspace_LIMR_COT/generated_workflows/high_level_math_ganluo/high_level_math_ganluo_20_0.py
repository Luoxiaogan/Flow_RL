# Workflow ID: high_level_math_ganluo_20_0
# Benchmark: high_level_math_ganluo
# Data Indices: [379, 331]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem # Assumes problem is a pre-processed string
        self.llm = create(config)

        # All available operators are initialized here for your use.
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        This is where you implement the core problem-solving logic.
        You can use any of the operators initialized above.
        """
        import asyncio

        # Step 1: Initial Analysis
        analysis = await self.generate("Analyze the problem structure. Is it primarily algebraic, geometric, combinatorial, or number-theoretic? Identify constraints and variables.")

        # Step 2: Parallel Exploration of Two Solution Strategies
        task1 = self.generate("Solve using algebraic manipulation and substitution. Derive equations step-by-step from the given conditions.")
        task2 = self.generate("Try a case-based or numerical approach. Assume small integer values for unknowns and test against constraints.")

        solutions = await asyncio.gather(task1, task2)

        # Step 3: Summarize Each Path
        summary1 = await self.summarize(solutions[0])
        summary2 = await self.summarize(solutions[1])

        # Step 4: Ensemble Final Answer
        final_answer = await self.ensemble(
            "Select the most consistent and mathematically sound solution based on both reasoning paths. Ensure it satisfies all original constraints.",
            [summary1, summary2]
        )

        return final_answer
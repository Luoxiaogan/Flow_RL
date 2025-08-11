# Workflow ID: high_level_math_ganluo_17_0
# Benchmark: high_level_math_ganluo
# Data Indices: [428, 978]

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

        # Step 1: Diverge — Generate 3 different solution approaches in parallel
        task1 = self.generate("Solve using direct algebraic manipulation and substitution.")
        task2 = self.generate("Explore if the problem has symmetric properties or can be modeled with Vieta's formulas.")
        task3 = self.generate("Try a case-based or bounding argument to narrow down possible integer solutions.")

        # Execute all strategies simultaneously
        results = await asyncio.gather(task1, task2, task3)

        # Step 2: Summarize each strategy to focus on key insights
        summaries = [await self.summarize(result) for result in results]

        # Step 3: Ensemble — Compare and synthesize the three candidate solutions
        final_answer = await self.ensemble(
            "Among these three approaches, which provides the most consistent and mathematically sound integer answer?",
            summaries
        )

        return final_answer
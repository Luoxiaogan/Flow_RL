# Workflow ID: high_level_math_ganluo_13_0
# Benchmark: high_level_math_ganluo
# Data Indices: [24, 253]

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

        # Step 1: Diverge — Generate multiple solution strategies in parallel
        task1 = self.generate("Approach using coordinate geometry: place rectangle ABCD on coordinate plane and compute slopes or angles.")
        task2 = self.generate("Approach using trigonometric identities: express tan(angle APD) in terms of side lengths AB and BC.")
        task3 = self.generate("Approach using similar triangles: identify if triangle APD relates to other triangles in the figure via similarity.")

        solutions = await asyncio.gather(task1, task2, task3)

        # Step 2: Converge — Summarize each strategy to extract key insights
        summaries = [
            await self.summarize(solutions[0]),
            await self.summarize(solutions[1]),
            await self.summarize(solutions[2])
        ]

        # Step 3: Ensemble — Compare and synthesize best approach
        final_answer = await self.ensemble(
            "Based on the three solution strategies, which one yields the correct integer answer between 0 and 999? Prioritize clarity, mathematical correctness, and internal consistency.",
            summaries
        )

        return final_answer
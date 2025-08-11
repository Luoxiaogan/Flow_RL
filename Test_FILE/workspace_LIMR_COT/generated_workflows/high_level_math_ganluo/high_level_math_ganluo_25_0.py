# Workflow ID: high_level_math_ganluo_25_0
# Benchmark: high_level_math_ganluo
# Data Indices: [1, 722]

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

        # Step 1: Parallel Exploration – Generate 3 different solution strategies
        task1 = self.generate("Generate a geometric approach to solve this problem.")
        task2 = self.generate("Generate an algebraic approach to solve this problem.")
        task3 = self.generate("Generate a combinatorial or probabilistic approach to solve this problem.")

        strategies = await asyncio.gather(task1, task2, task3)

        # Step 2: Summarize each strategy for clarity and context control
        summary1 = await self.summarize(strategies[0])
        summary2 = await self.summarize(strategies[1])
        summary3 = await self.summarize(strategies[2])

        # Step 3: Ensemble final answer based on consistency and validity
        final_answer = await self.ensemble(
            "Based on the three solution strategies, determine the correct integer answer between 0 and 999.",
            [summary1, summary2, summary3]
        )

        return final_answer
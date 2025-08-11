# Workflow ID: high_level_math_ganluo_29_0
# Benchmark: high_level_math_ganluo
# Data Indices: [874, 665]

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
        task1 = self.generate("Solve using algebraic manipulation")
        task2 = self.generate("Solve using number theory techniques")
        task3 = self.generate("Solve using combinatorics or counting principles")
        task4 = self.generate("Solve using geometric interpretation")

        results = await asyncio.gather(task1, task2, task3, task4)

        # Step 2: Extract key insights from each approach
        summaries = [
            await self.summarize(result) for result in results
        ]

        # Step 3: Converge — Ensemble to select best solution
        final_answer = await self.ensemble(
            "Select the most consistent and mathematically sound answer across all approaches.",
            summaries
        )

        # Step 4: Optional refinement — Revise if needed to ensure correctness
        refined_answer = await self.revise(
            "Verify that the selected answer satisfies all constraints of the original problem.",
            final_answer
        )

        return refined_answer
# Workflow ID: high_level_math_ganluo_30_0
# Benchmark: high_level_math_ganluo
# Data Indices: [873, 882]

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
        task1 = self.generate("Approach this as an algebraic problem: identify variables and equations.")
        task2 = self.generate("Approach this as a geometric problem: look for symmetries or coordinate-based representations.")
        task3 = self.generate("Approach this as a combinatorial problem: consider cases, constraints, and counting principles.")
        task4 = self.generate("Approach this as a probabilistic problem: if applicable, compute expected values or probabilities.")

        solutions = await asyncio.gather(task1, task2, task3, task4)

        # Step 2: Converge — Summarize each solution to extract key elements
        summaries = [
            await self.summarize(solutions[0]),
            await self.summarize(solutions[1]),
            await self.summarize(solutions[2]),
            await self.summarize(solutions[3])
        ]

        # Step 3: Ensemble — Synthesize the top candidates into a single answer
        final_answer = await self.ensemble(
            "Select the most consistent integer answer between 0 and 999 that emerges from all perspectives.",
            summaries
        )

        return final_answer
# Workflow ID: high_level_math_ganluo_26_0
# Benchmark: high_level_math_ganluo
# Data Indices: [98, 972]

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

        # Step 1: Diverge – Generate 3 different solution strategies in parallel
        task1 = self.generate("Solve using algebraic manipulation", "")
        task2 = self.generate("Solve using modular arithmetic", "")
        task3 = self.generate("Solve using case analysis and symmetry", "")

        solutions = await asyncio.gather(task1, task2, task3)

        # Step 2: Converge – Summarize each solution path
        summaries = [
            await self.summarize(solutions[0]),
            await self.summarize(solutions[1]),
            await self.summarize(solutions[2])
        ]

        # Step 3: Ensemble – Compare summaries to pick best candidate
        final_answer = await self.ensemble(
            "Select the most mathematically consistent and complete solution from these three approaches.",
            summaries
        )

        # Step 4: Verify – Revise final answer for correctness and boundary conditions
        verified_answer = await self.revise(
            "Check if the selected answer satisfies all constraints in the original problem statement.",
            final_answer
        )

        return verified_answer
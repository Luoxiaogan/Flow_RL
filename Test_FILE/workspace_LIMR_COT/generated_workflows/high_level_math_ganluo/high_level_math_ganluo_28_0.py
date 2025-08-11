# Workflow ID: high_level_math_ganluo_28_0
# Benchmark: high_level_math_ganluo
# Data Indices: [401, 205]

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

        # Step 1: Initial analysis — detect likely problem category
        analysis = await self.generate(
            instruction="Identify the primary mathematical domain of this problem (e.g., algebra, geometry, number theory, combinatorics)."
        )

        # Step 2: Parallel exploration — generate 3 different solution paths
        task1 = self.generate("Solve using direct algebraic manipulation.")
        task2 = self.generate("Solve using coordinate geometry / vector methods.")
        task3 = self.generate("Solve using modular arithmetic or symmetry arguments.")

        results = await asyncio.gather(task1, task2, task3)

        # Step 3: Summarize each path for clarity and context management
        summaries = [
            await self.summarize(results[0]),
            await self.summarize(results[1]),
            await self.summarize(results[2])
        ]

        # Step 4: Ensemble final answer — compare and synthesize
        final_answer = await self.ensemble(
            instruction="Choose the correct integer answer between 0 and 999 that is consistently supported by all solution paths.",
            contexts_to_ensemble=summaries
        )

        return final_answer
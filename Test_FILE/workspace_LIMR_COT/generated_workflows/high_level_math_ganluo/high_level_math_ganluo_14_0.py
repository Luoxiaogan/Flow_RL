# Workflow ID: high_level_math_ganluo_14_0
# Benchmark: high_level_math_ganluo
# Data Indices: [216, 481]

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

        # Step 1: Analyze problem structure
        analysis = await self.generate("Identify the category of this problem (e.g., algebra, number theory, geometry) and list all given constraints.")

        # Step 2: Generate multiple solution paths in parallel
        task1 = self.generate("Solve using algebraic manipulation: factor, substitute, or isolate variables.")
        task2 = self.generate("Apply number theory techniques: check modular arithmetic, divisibility, or Diophantine methods.")
        task3 = self.generate("Explore geometric or coordinate-based interpretations if applicable.")

        results = await asyncio.gather(task1, task2, task3)

        # Step 3: Summarize each candidate solution
        summaries = [
            await self.summarize(results[0]),
            await self.summarize(results[1]),
            await self.summarize(results[2])
        ]

        # Step 4: Ensemble final answer
        final_answer = await self.ensemble(
            "Choose the most consistent and mathematically valid solution among these candidates.",
            summaries
        )

        return final_answer
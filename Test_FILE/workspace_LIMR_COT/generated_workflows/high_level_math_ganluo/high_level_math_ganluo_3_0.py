# Workflow ID: high_level_math_ganluo_3_0
# Benchmark: high_level_math_ganluo
# Data Indices: [439, 290]

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

        # Step 1: Initial Analysis — Understand the nature of the problem
        analysis = await self.generate("What type of mathematical problem is this? Identify key categories like number theory, combinatorics, geometry, etc.")

        # Step 2: Parallel Exploration — Generate three different solution strategies
        task1 = self.generate("Solve directly using basic arithmetic operations and case enumeration.")
        task2 = self.generate("Apply modular arithmetic or divisibility rules if applicable.")
        task3 = self.generate("Consider recursive structures or generating functions if combinatorics is involved.")

        results = await asyncio.gather(task1, task2, task3)

        # Step 3: Summarize each candidate solution to extract essential logic
        summaries = [
            await self.summarize(result) for result in results
        ]

        # Step 4: Ensemble the summaries to reach a final, robust conclusion
        final_answer = await self.ensemble(
            "Select the most consistent and logically sound solution among the candidates.",
            summaries
        )

        return final_answer
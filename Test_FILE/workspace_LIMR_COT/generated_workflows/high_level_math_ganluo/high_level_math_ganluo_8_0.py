# Workflow ID: high_level_math_ganluo_8_0
# Benchmark: high_level_math_ganluo
# Data Indices: [417, 689]

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

        # Step 1: Parallel Exploration – Generate 3 distinct solution strategies
        task1 = self.generate("Generate an algebraic solution path based on equation structure.")
        task2 = self.generate("Generate a number-theoretic approach focusing on divisibility or modular constraints.")
        task3 = self.generate("Generate a casework or symmetry-based solution strategy.")

        # Execute in parallel
        paths = await asyncio.gather(task1, task2, task3)

        # Step 2: Summarize each path for clarity and context compression
        summary1 = await self.summarize(paths[0])
        summary2 = await self.summarize(paths[1])
        summary3 = await self.summarize(paths[2])

        # Step 3: Ensemble to select the most consistent and plausible answer
        ensemble_result = await self.ensemble(
            "Compare the three solution paths and select the most logically sound and mathematically consistent answer.",
            [summary1, summary2, summary3]
        )

        # Step 4: Optional Iterative Refinement if ensemble is vague or uncertain
        # Check for uncertainty signals like "multiple possible answers" or "ambiguous"
        if "uncertain" in ensemble_result.lower() or "ambiguous" in ensemble_result.lower():
            revised = await self.revise(
                "Refine the solution by checking edge cases, verifying constraints, and ensuring no contradictions exist.",
                context_to_revise=ensemble_result
            )
            return revised.strip()

        return ensemble_result.strip()
# Workflow ID: high_level_math_ganluo_7_0
# Benchmark: high_level_math_ganluo
# Data Indices: [581, 500]

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

        # Step 1: Extract and summarize key elements from the problem
        summary = await self.summarize(self.problem_text)

        # Step 2: Generate multiple distinct solution strategies in parallel
        task1 = self.generate("Approach 1: Use coordinate geometry to model the shape.", context=summary)
        task2 = self.generate("Approach 2: Unwrap the surface (e.g., cylinder into rectangle) to find straight-line path.", context=summary)
        task3 = self.generate("Approach 3: Apply symmetry or known formulas (e.g., distance in regular polygons).", context=summary)

        approaches = await asyncio.gather(task1, task2, task3)

        # Step 3: Ensemble to select the best solution based on consistency and clarity
        final_answer = await self.ensemble(
            "Select the most mathematically sound and consistent solution among the three approaches.",
            approaches
        )

        # Optional: If ensemble result seems ambiguous, refine with revision
        if "ambiguous" in final_answer.lower() or "multiple" in final_answer.lower():
            final_answer = await self.revise(
                "Refine the solution by checking all constraints again and resolving contradictions between approaches.",
                final_answer
            )

        return final_answer
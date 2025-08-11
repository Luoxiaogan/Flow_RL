# Workflow ID: high_level_math_ganluo_32_0
# Benchmark: high_level_math_ganluo
# Data Indices: [810, 44]

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

        # Step 1: Initial analysis to detect dominant mathematical domain
        analysis = await self.generate("Identify the primary mathematical domain (algebra, geometry, number theory, combinatorics, or mixed) of this problem.")
        
        # Step 2: Parallel exploration of three distinct solution strategies
        task1 = self.generate("Solve using algebraic manipulation and simplification techniques.")
        task2 = self.generate("Solve using geometric interpretation or coordinate bashing.")
        task3 = self.generate("Solve using number-theoretic methods like modular arithmetic or divisibility rules.")

        results = await asyncio.gather(task1, task2, task3)

        # Step 3: Summarize each solution path for comparison
        summary1 = await self.summarize(results[0])
        summary2 = await self.summarize(results[1])
        summary3 = await self.summarize(results[2])

        # Step 4: Ensemble to select best-supported solution path
        ensemble_result = await self.ensemble(
            "Compare the three solution paths and identify the one that satisfies all constraints and makes the most mathematical sense.",
            [summary1, summary2, summary3]
        )

        # Step 5: Optional refinement if ensemble result lacks clarity
        if "uncertain" in ensemble_result.lower() or "ambiguous" in ensemble_result.lower():
            refined = await self.revise(
                "Critique the selected solution path and improve precision by checking edge cases and verifying integer bounds (0–999).",
                ensemble_result
            )
            return refined.strip()

        # Final step: Return the clean integer answer
        return ensemble_result.strip()
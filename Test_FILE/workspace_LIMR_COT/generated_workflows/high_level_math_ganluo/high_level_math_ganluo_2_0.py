# Workflow ID: high_level_math_ganluo_2_0
# Benchmark: high_level_math_ganluo
# Data Indices: [306, 285]

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

        # Step 1: Understand the problem type
        analysis = await self.generate("Identify the primary mathematical domain (algebra, geometry, number theory, combinatorics, etc.) and key constraints from this problem.")
        
        # Step 2: Generate multiple solution strategies in parallel
        task1 = self.generate("Solve using algebraic simplification and substitution.", context=analysis)
        task2 = self.generate("Explore symmetry or pattern-based reasoning if applicable.", context=analysis)
        task3 = self.generate("Apply modular arithmetic or divisibility rules if relevant.", context=analysis)
        
        solutions = await asyncio.gather(task1, task2, task3)

        # Step 3: Summarize each solution path
        summaries = [await self.summarize(sol) for sol in solutions]

        # Step 4: Ensemble to find the most consistent answer
        final_answer = await self.ensemble(
            "Choose the most mathematically sound and consistent answer among these approaches.",
            summaries
        )

        # Step 5: Optional refinement if ensemble result seems uncertain
        if "likely" in final_answer.lower() or "ambiguous" in final_answer.lower():
            revised = await self.revise(
                "Refine the answer by checking for common errors such as incorrect signs, missing factors, or misapplied formulas.",
                context_to_revise=final_answer
            )
            final_answer = revised

        return final_answer
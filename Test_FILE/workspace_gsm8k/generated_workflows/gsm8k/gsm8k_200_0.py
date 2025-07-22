# Workflow ID: gsm8k_200_0
# Benchmark: gsm8k
# Data Indices: [384, 31]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on its weaknesses or assumptions.
        4. Use that reflection to guide a new Custom call for an improved solution.
        This creates a meta-cognitive loop with diversity in initial reasoning and refinement.
        """
        # Step 1: Parallel Ensemble - Generate multiple candidate solutions
        solution_candidates = []
        for i in range(3):
            instruction = f"Approach the problem from a different perspective: {['step-by-step', 'formula-based', 'visual analogy'][i]}"
            candidate = await self.custom(instruction=instruction)
            solution_candidates.append(candidate)

        # Step 2: Select the best solution
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect on the selected solution to identify potential flaws
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to generate a final refined solution
        final_instruction = (
            "Given the following initial solution and reflection, "
            "provide a more accurate and robust answer:\n\n"
            f"Initial Solution:\n{best_solution}\n\n"
            f"Reflection (potential issues or improvements):\n{reflection}"
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution
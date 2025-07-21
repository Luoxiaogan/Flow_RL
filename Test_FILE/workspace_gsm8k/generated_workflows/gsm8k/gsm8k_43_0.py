# Workflow ID: gsm8k_43_0
# Benchmark: gsm8k
# Data Indices: [368, 268]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect critically on it to uncover hidden assumptions or errors.
        4. Use reflection to guide a new Custom call for an improved solution.
        """
        # --- Step 1: Parallel Ensemble ---
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step by breaking it into clear sub-problems. Be thorough and avoid skipping steps."
            )
            solution_candidates.append(candidate)

        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Step 2: Reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 3: Conditional logic based on reflection ---
        # If reflection indicates potential issues (e.g., mentions uncertainty), regenerate
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower() or "error" in reflection.lower():
            final_solution = await self.custom(
                instruction=f"Based on the following reflection, improve the solution: {reflection}. Focus on correcting any identified flaws."
            )
        else:
            # If no major issues found, use the best solution directly
            final_solution = best_solution

        return final_solution
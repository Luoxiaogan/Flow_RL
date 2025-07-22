# Workflow ID: gsm8k_264_0
# Benchmark: gsm8k
# Data Indices: [129, 72]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on it to identify potential flaws or improvements.
        Step 4: Use reflection to guide a new Custom solution for final refinement.
        """
        # --- PARALLEL ENSEMBLE ---
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem by breaking it into logical steps. Be precise and avoid assumptions.")
            solutions.append(sol)

        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT ON BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- USE REFLECTION TO GUIDED REGENERATION ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution: {best_solution}. "
                        f"And the following reflection on its limitations: {reflection}. "
                        "Now, provide a revised, improved solution that addresses these points."
        )

        return final_answer
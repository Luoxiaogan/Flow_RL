# Workflow ID: gsm8k_397_0
# Benchmark: gsm8k
# Data Indices: [149, 692, 433]

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
        Step 2: Pick the best one using ScEnsemble.
        Step 3: Reflect on it to identify potential flaws or missed assumptions.
        Step 4: Use that reflection to guide a new Custom call for an improved solution.
        This creates a meta-cognitive loop with diversity in both initial exploration and refinement.
        """

        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solution_pool = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step. Break it into parts and explain each clearly.")
            solution_pool.append(sol)

        # --- SCENSEMBLE (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- REFLECT ON BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- USE REFLECTION TO REGENERATE A BETTER SOLUTION ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Use this insight to generate a more accurate and complete answer."
        )

        return final_answer
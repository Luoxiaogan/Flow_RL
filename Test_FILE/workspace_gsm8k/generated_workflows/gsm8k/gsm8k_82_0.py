# Workflow ID: gsm8k_82_0
# Benchmark: gsm8k
# Data Indices: [271, 492]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions using parallel approach.
        Step 2: Use ScEnsemble to select the best one.
        Step 3: Reflect on that solution for potential flaws or missed logic.
        Step 4: Use reflection to guide a new Custom call for an improved answer.
        """

        # --- PARALLEL ENSEMBLE: Generate multiple initial attempts ---
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step. Focus on identifying key quantities and relationships."
            )
            solution_candidates.append(candidate)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REFLECT ON THE BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- USE REFLECTION TO GUIDED REGENERATION ---
        final_answer = await self.custom(
            instruction=f"Given the following solution: {best_solution}. "
                        f"And here is a critical reflection on it: {reflection}. "
                        f"Based on this reflection, re-solve the problem with improved reasoning and clarity."
        )

        return final_answer
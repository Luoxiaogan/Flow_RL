# Workflow ID: gsm8k_94_0
# Benchmark: gsm8k
# Data Indices: [706, 167]

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
        Step 1: Generate 3 independent solutions using parallel approach.
        Step 2: Select best solution via ScEnsemble.
        Step 3: Reflect on its weaknesses or assumptions.
        Step 4: Use reflection to guide a new Custom call for final refinement.
        """
        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solutions = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step. Focus on clarity, accuracy, and logical structure."
            )
            solutions.append(solution)

        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT AND REGENERATE (Meta-cognitive loop) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # Conditional logic based on reflection content — if it mentions uncertainty, we regenerate
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower():
            final_answer = await self.custom(
                instruction=f"Based on the following reflection: '{reflection}'. Re-solve the problem with improved reasoning, addressing potential flaws or missing steps."
            )
        else:
            final_answer = await self.review(pre_solution=best_solution)

        return final_answer
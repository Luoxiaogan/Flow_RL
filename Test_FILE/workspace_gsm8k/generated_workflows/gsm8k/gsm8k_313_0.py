# Workflow ID: gsm8k_313_0
# Benchmark: gsm8k
# Data Indices: [20, 758]

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
        1. Generate multiple candidate solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect critically on its weaknesses or assumptions.
        4. Use that reflection to guide a new solution generation (regeneration).
        """
        # --- Step 1: Parallel Ensemble — Generate 3 independent solutions ---
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve this math problem step-by-step with clear reasoning. Focus on identifying key operations and constraints."
            )
            solution_candidates.append(candidate)

        # --- Step 2: Evaluate and select the best candidate ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Step 3: Reflect on the selected solution — critique it without rewriting ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate a better solution based on reflection ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution below and the following reflection about potential flaws or improvements:\n\n{reflection}\n\nPlease now provide an improved, more robust solution that addresses these points."
        )

        return final_answer
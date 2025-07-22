# Workflow ID: gsm8k_156_0
# Benchmark: gsm8k
# Data Indices: [941, 133, 549]

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
        3. Reflect on its weaknesses or assumptions.
        4. Use that reflection to guide a new Custom call for a refined solution.
        This ensures both robustness (from ensembling) and meta-cognitive improvement (from reflection).
        """
        # --- STEP 1: Generate multiple solutions in parallel ---
        solution_list = []
        for i in range(3):  # Parallel ensemble with 3 attempts
            solution = await self.custom(
                instruction="Solve the problem step-by-step, breaking it into logical sub-problems. Be thorough and explicit about each calculation."
            )
            solution_list.append(solution)

        # --- STEP 2: Pick the best solution using ensemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Critically reflect on the best solution ---
        reflection_text = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate a better solution based on reflection ---
        final_solution = await self.custom(
            instruction=f"Given the initial solution: {best_solution}. "
                        f"And the following reflection on potential flaws or missed steps: {reflection_text}. "
                        "Now, provide a revised, more accurate and complete solution."
        )

        return final_solution
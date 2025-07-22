# Workflow ID: gsm8k_172_0
# Benchmark: gsm8k
# Data Indices: [394, 896, 315]

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
        2. Select the best solution using ScEnsemble.
        3. Reflect on its potential flaws or assumptions.
        4. Use reflection to guide a targeted regenerative step for improvement.
        5. Final review ensures clarity and correctness.
        """

        # --- Step 1: Parallel Ensemble (Fan-out) ---
        solution_pool = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve the problem by breaking it into clear steps. Focus on arithmetic accuracy and logical structure."
            )
            solution_pool.append(sol)

        # --- Step 2: Choose the best candidate ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- Step 3: Reflect on the best solution (meta-cognitive critique) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate based on reflection (Reflect-and-Regenerate Pattern) ---
        improved_instruction = (
            "Given the initial solution and the following reflection:\n"
            f"{reflection}\n\n"
            "Now, provide a new, improved solution that addresses any issues raised in the reflection. "
            "Ensure all steps are explicit, logically sound, and mathematically accurate."
        )
        final_solution = await self.custom(instruction=improved_instruction)

        # --- Step 5: Final Review for polish and clarity ---
        polished_solution = await self.review(pre_solution=final_solution)

        return polished_solution
# Workflow ID: gsm8k_100_0
# Benchmark: gsm8k
# Data Indices: [354, 866]

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
        4. Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- Step 1: Parallel Ensemble (Fan-out) ---
        solution_pool = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, showing all calculations clearly.")
            solution_pool.append(sol)

        # --- Step 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- Step 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate Using Reflection as Guidance ---
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again, focusing on addressing potential flaws or missed details.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        return final_solution
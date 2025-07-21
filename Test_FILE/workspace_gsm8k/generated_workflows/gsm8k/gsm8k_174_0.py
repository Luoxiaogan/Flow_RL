# Workflow ID: gsm8k_174_0
# Benchmark: gsm8k
# Data Indices: [876, 672]

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
        1. Generate 3 independent solutions via parallel ensemble (robustness).
        2. Select the best solution using ScEnsemble.
        3. Reflect on that solution to identify potential blind spots or assumptions.
        4. Use reflection to guide a new, improved Custom solution.
        """
        # --- Step 1: Parallel Ensemble ---
        solutions = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve this math problem by breaking it into clear steps. Focus on identifying knowns, unknowns, and applying relevant formulas."
            )
            solutions.append(sol)

        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 2: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 3: Regenerate with Reflection Guidance ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution: {best_solution}, and the following reflection on its potential weaknesses or missing elements: {reflection}. Now, provide a revised and more robust solution."
        )

        return final_answer
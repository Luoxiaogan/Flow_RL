# Workflow ID: gsm8k_84_0
# Benchmark: gsm8k
# Data Indices: [61, 40]

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
        3. Reflect critically on its assumptions and potential flaws.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom (iterative pattern).
        """
        # --- Step 1: Parallel Ensemble ---
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, focusing on clear reasoning and identifying key variables.")
            solutions.append(sol)

        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 2: Reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 3: Conditional Regeneration Based on Reflection ---
        if "assumption" in reflection.lower() or "error" in reflection.lower():
            # If reflection identifies issues, use iterative refinement via FlexibleCustom
            improved_solution = await self.flexible_custom(
                custom_instruction="Re-solve the problem by addressing the following reflection: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze_reflection", "adjust_assumptions", "recompute"],
                max_iterations=2
            )
        else:
            # If no major issues, just refine with Review
            improved_solution = await self.review(pre_solution=best_solution)

        return improved_solution
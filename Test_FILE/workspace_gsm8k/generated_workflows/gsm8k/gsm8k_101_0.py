# Workflow ID: gsm8k_101_0
# Benchmark: gsm8k
# Data Indices: [569, 646]

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
        Diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on its weaknesses or assumptions.
        4. Use reflection to guide a new, improved solution via FlexibleCustom (iterative pattern).
        """
        # Step 1: Parallel Ensemble — generate multiple candidate solutions
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, showing all calculations and reasoning clearly.")
            solutions.append(sol)

        # Step 2: Choose the best solution from the ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the chosen solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new, refined solution via iterative FlexibleCustom
        refined_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection: " + reflection,
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_assumptions", "recompute", "verify"],
            max_iterations=2
        )

        return refined_solution
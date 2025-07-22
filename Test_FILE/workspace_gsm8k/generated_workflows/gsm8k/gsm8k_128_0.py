# Workflow ID: gsm8k_128_0
# Benchmark: gsm8k
# Data Indices: [769, 54]

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
        Diverse workflow combining Parallel Ensemble + Reflect and Regenerate.
        1. Generate multiple solutions via parallel ensemble.
        2. Select best solution using ScEnsemble.
        3. Reflect on its potential flaws or assumptions.
        4. Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # Step 1: Generate 3 independent solutions in parallel (Parallel Ensemble pattern)
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, explaining each reasoning stage clearly.")
            solutions.append(sol)

        # Step 2: Pick the best one from the ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the selected solution — no rewriting yet
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, generate an improved solution using FlexibleCustom with iterative refinement
        # This uses "iterative" reasoning pattern to refine based on critique
        improved_solution = await self.flexible_custom(
            custom_instruction="Use the following reflection to improve the solution: " + reflection,
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_reasoning", "recompute"],
            max_iterations=2
        )

        return improved_solution
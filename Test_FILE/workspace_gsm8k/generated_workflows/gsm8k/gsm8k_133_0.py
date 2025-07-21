# Workflow ID: gsm8k_133_0
# Benchmark: gsm8k
# Data Indices: [950, 710]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on its potential flaws or missed assumptions.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # Step 1: Parallel Ensemble — generate multiple initial approaches
        solutions = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step using a different reasoning strategy each time (e.g., algebraic, unit-based, or proportional)."
            )
            solutions.append(sol)

        # Step 2: Pick the best solution from the ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution — identify weaknesses or gaps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a better solution based on the reflection
        final_solution = await self.flexible_custom(
            custom_instruction=f"Given the following reflection on the previous solution: '{reflection}'. Now solve the problem again with deeper analysis, ensuring no assumptions are left unchallenged.",
            reasoning_pattern="iterative",
            steps=["analyze_assumptions", "reconstruct_reasoning", "verify_with_examples"],
            max_iterations=2
        )

        return final_solution
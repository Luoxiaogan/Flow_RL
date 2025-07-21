# Workflow ID: gsm8k_134_1
# Benchmark: gsm8k
# Data Indices: [701, 68]

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
        1. Generate 3 independent solutions using FlexibleCustom in 'parallel' mode.
        2. Use ScEnsemble to select the best one.
        3. Reflect on that solution to identify potential flaws or improvements.
        4. Regenerate a final answer based on the reflection — this mimics meta-cognition and adaptive reasoning.
        This pattern improves robustness (via ensembling) and adaptability (via reflection).
        """
        # Step 1: Generate multiple candidate solutions via parallel ensemble
        solutions = []
        for _ in range(3):
            sol = await self.flexible_custom(
                custom_instruction="Solve the problem by first identifying key operations, then computing step-by-step.",
                reasoning_pattern="parallel",
                steps=["identify_operations", "compute_step_by_step", "check_consistency"]
            )
            solutions.append(sol)

        # Step 2: Select the best solution from the ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a refined solution informed by the reflection
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity and accuracy."
        )

        return final_answer
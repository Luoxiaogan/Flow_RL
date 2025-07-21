# Workflow ID: gsm8k_0_0
# Benchmark: gsm8k
# Data Indices: [476, 238, 594]

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
        Step 1: Generate multiple initial solutions (Parallel Ensemble).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on the selected solution to uncover hidden assumptions or errors.
        Step 4: Use reflection to guide a new, improved Custom solution.
        This ensures robustness via ensembling and meta-cognition via reflection.
        """
        # --- PARALLEL ENSEMBLE ---
        solution_candidates = []
        for _ in range(3):  # Generate 3 different approaches
            candidate = await self.custom(
                instruction="Solve this math problem by breaking it into steps. Think of multiple ways to approach it."
            )
            solution_candidates.append(candidate)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REFLECT ON THE BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE WITH REFLECTION GUIDANCE ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        "Now, solve the problem again, incorporating insights from the reflection to improve accuracy."
        )

        return final_answer
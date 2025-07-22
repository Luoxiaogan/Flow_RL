# Workflow ID: gsm8k_293_0
# Benchmark: gsm8k
# Data Indices: [49, 929]

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
        This is a diverse workflow combining Parallel Ensemble + Reflect and Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on that solution to uncover potential blind spots or assumptions.
        Step 4: Use the reflection to guide a new, improved Custom call for final answer.
        """

        # --- PARALLEL ENSEMBLE ---
        solutions = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step, breaking it into logical parts. Avoid assuming anything not stated."
            )
            solutions.append(solution)

        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT AND REGENERATE ---
        reflection = await self.reflect(pre_solution=best_solution)

        # Conditional logic based on reflection content (e.g., if reflection mentions ambiguity, we regenerate with clearer constraints)
        if "assumption" in reflection.lower() or "ambiguity" in reflection.lower():
            final_answer = await self.custom(
                instruction=f"Based on the following reflection: '{reflection}'. Re-solve the problem with more rigorous reasoning, focusing on eliminating assumptions."
            )
        else:
            final_answer = await self.custom(
                instruction=f"Given the initial solution and this reflection: '{reflection}'. Now provide a refined, confident answer."
            )

        return final_answer
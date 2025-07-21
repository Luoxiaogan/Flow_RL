# Workflow ID: gsm8k_13_0
# Benchmark: gsm8k
# Data Indices: [843, 419]

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
        self.reflect = operator.Reflect(selfconfig, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions using parallel approach.
        Step 2: Select the best one via ScEnsemble.
        Step 3: Reflect critically on it to uncover hidden assumptions or errors.
        Step 4: Use reflection to guide a targeted regeneration for an improved final answer.
        """
        # --- PARALLEL ENSEMBLE (Fan-out) ---
        solution_list = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly. Focus on identifying constraints and applying operations in logical order.")
            solution_list.append(sol)

        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- REFLECT AND REGENERATE (Meta-cognitive loop) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # Conditional logic based on reflection content — e.g., if reflection mentions "assumption about units" or "missing constraint", we regenerate accordingly
        if "assumption" in reflection.lower() or "constraint" in reflection.lower():
            final_answer = await self.flexible_custom(
                custom_instruction="Based on the following reflection, improve the solution by addressing potential flaws or overlooked details: " + reflection,
                previous_results=[best_solution]
            )
        else:
            # If no major flaw detected, just refine with Review
            final_answer = await self.review(pre_solution=best_solution)

        return final_answer
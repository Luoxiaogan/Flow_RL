# Workflow ID: gsm8k_129_0
# Benchmark: gsm8k
# Data Indices: [488, 708]

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
        2. Select the best solution using ScEnsemble.
        3. Reflect on its potential weaknesses or assumptions.
        4. Use that reflection to guide a targeted re-generation of the final answer.
        """
        # --- Step 1: Parallel Ensemble ---
        solution_list = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, showing all calculations clearly.")
            solution_list.append(sol)

        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 2: Reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 3: Conditional Regeneration Based on Reflection ---
        if "assumption" in reflection.lower() or "unclear" in reflection.lower():
            # If reflection highlights flaws, regenerate with guidance
            final_answer = await self.custom(
                instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                            f"Re-solve the problem carefully, addressing any gaps or unclear logic."
            )
        else:
            # If reflection is neutral or positive, use it as-is or refine lightly
            final_answer = await self.review(pre_solution=best_solution)

        return final_answer
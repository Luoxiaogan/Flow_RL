# Workflow ID: gsm8k_18_0
# Benchmark: gsm8k
# Data Indices: [462, 326]

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
        3. Critically reflect on it to uncover hidden assumptions or errors.
        4. Use that reflection to guide a new Custom call for final refinement.
        """
        # --- Step 1: Parallel Ensemble ---
        solution_list = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve this math problem by considering multiple possible interpretations of the scenario. Be thorough."
            )
            solution_list.append(sol)

        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 2: Reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 3: Conditional Regeneration based on Reflection ---
        if "assumption" in reflection.lower() or "error" in reflection.lower() or "unclear" in reflection.lower():
            # If reflection suggests flaws, regenerate with targeted guidance
            final_answer = await self.custom(
                instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                            f"Re-solve the problem while explicitly addressing these points. Show your reasoning step-by-step."
            )
        else:
            # If reflection is neutral or positive, just return the best solution
            final_answer = best_solution

        return final_answer
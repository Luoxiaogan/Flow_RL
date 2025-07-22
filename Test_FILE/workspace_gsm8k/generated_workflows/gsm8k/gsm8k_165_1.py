# Workflow ID: gsm8k_165_1
# Benchmark: gsm8k
# Data Indices: [753, 190, 50]

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
        This is a diverse and robust workflow using the Iterative Refinement pattern.
        It generates an initial solution, then applies Review twice to progressively improve it.
        This mimics how humans refine reasoning through multiple passes — not just one attempt.
        """

        # --- Step 1: Generate an initial solution with clear step-by-step instructions ---
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Be explicit about each calculation."
        )

        # --- Step 2: First refinement via Review ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second refinement via Review (more focused on clarity and correctness) ---
        second_refined = await self.review(pre_solution=first_refined)

        # --- Optional: Use Reflect to analyze the final solution for hidden assumptions or gaps ---
        reflection = await self.reflect(pre_solution=second_refined)

        # --- Final check: If reflection suggests issues, regenerate with guided instruction ---
        if "error" in reflection.lower() or "assumption" in reflection.lower():
            final_answer = await self.custom(
                instruction=f"Based on the following reflection: {reflection}. Now, provide a corrected and improved solution."
            )
        else:
            final_answer = second_refined

        return final_answer
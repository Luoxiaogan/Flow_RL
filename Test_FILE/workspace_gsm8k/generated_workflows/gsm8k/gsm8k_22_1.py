# Workflow ID: gsm8k_22_1
# Benchmark: gsm8k
# Data Indices: [954, 835, 909]

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
        It starts with a simple initial solution, then applies Review twice to progressively improve clarity, correctness, and completeness.
        This mimics how humans refine their thinking through multiple passes — first identifying flaws, then fixing them.
        """
        # --- Step 1: Generate an initial solution using a straightforward approach ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear but concise."
        )

        # --- Step 2: First refinement pass — identify issues and rewrite for clarity ---
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second refinement pass — ensure logical consistency and completeness ---
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        # --- Optional: Use Reflect to understand why improvements were made (meta-cognition) ---
        reflection = await self.reflect(pre_solution=refined_solution_2)

        # --- Final step: Generate a polished version informed by both review and reflection ---
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, provide a fully revised, accurate, and well-explained solution."
        )

        return final_answer
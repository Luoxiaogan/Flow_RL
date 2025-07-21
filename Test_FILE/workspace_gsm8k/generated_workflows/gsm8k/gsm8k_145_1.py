# Workflow ID: gsm8k_145_1
# Benchmark: gsm8k
# Data Indices: [657, 388]

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
        It starts with an initial solution, then applies two rounds of review to progressively improve clarity, accuracy, and completeness.
        This mimics how humans refine their thinking through repeated self-assessment and correction.
        """

        # --- Step 1: Generate an initial solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Be concise but thorough."
        )

        # --- Step 2: First refinement via Review ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second refinement via Review ---
        second_refined = await self.review(pre_solution=first_refined)

        # --- Optional: Add a final reflective check for meta-awareness ---
        reflection = await self.reflect(pre_solution=second_refined)
        
        # --- Final polish based on reflection (optional but adds depth) ---
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about potential flaws or improvements in the current solution: '{reflection}'. "
                        f"Provide a final, polished version of the answer that addresses these points."
        )

        return final_answer
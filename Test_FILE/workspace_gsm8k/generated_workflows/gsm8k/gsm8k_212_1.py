# Workflow ID: gsm8k_212_1
# Benchmark: gsm8k
# Data Indices: [114, 302, 913]

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
        Efficient, single-pass solution with reflective critique and optional refinement.
        Uses a flexible custom operator in 'sequential' mode for structured reasoning,
        then applies reflection to identify potential blind spots before finalizing.
        This avoids redundant ensembling while maintaining robustness through meta-cognition.
        """

        # --- STEP 1: Generate a structured solution using FlexibleCustom ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear logical steps.",
            reasoning_pattern="sequential",
            steps=["understand_problem", "extract_knowns", "apply_math", "validate"]
        )

        # --- STEP 2: Reflect on the solution to uncover hidden assumptions or errors ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Use reflection to guide a targeted improvement (if needed) ---
        # If reflection indicates issues, regenerate with guidance; otherwise, return as-is
        if "error" in reflection.lower() or "assumption" in reflection.lower():
            final_answer = await self.custom(
                instruction=f"Based on the following reflection: {reflection}. Now, provide a corrected and improved solution."
            )
        else:
            final_answer = initial_solution

        return final_answer
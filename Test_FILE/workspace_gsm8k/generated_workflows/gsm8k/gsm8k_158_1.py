# Workflow ID: gsm8k_158_1
# Benchmark: gsm8k
# Data Indices: [508, 346, 4]

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
        Diverse and complex workflow combining Iterative Refinement + Reflect-and-Regenerate.
        Step 1: Use FlexibleCustom in iterative mode to generate a progressively refined solution.
        Step 2: After refinement, apply Reflect to critique the final result for hidden assumptions or edge cases.
        Step 3: If reflection indicates potential issues (e.g., "assumption about integer division"), trigger a targeted Custom call to fix it — this is a conditional regeneration based on content analysis.
        This mimics expert problem-solving: iterative improvement → meta-critique → targeted correction.

        Key differences from existing:
          - Uses iterative pattern via FlexibleCustom instead of parallel ensemble
          - Introduces conditional logic based on reflection content (not just blind regen)
          - Avoids ScEnsemble entirely; focuses on internal refinement and critical feedback
        """

        # --- ITERATIVE REFINEMENT USING FLEXIBLECUSTOM ---
        iterative_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_guess", "check_consistency", "adjust_for_constraints"],
            max_iterations=3,
            custom_instruction="Solve the problem step-by-step. Assume nothing until verified."
        )

        # --- REFLECT TO IDENTIFY FLAWS OR ASSUMPTIONS ---
        reflection = await self.reflect(pre_solution=iterative_solution)

        # --- CONDITIONAL REGENERATION BASED ON REFLECTION CONTENT ---
        if "assumption" in reflection.lower() or "edge case" in reflection.lower() or "integer" in reflection.lower():
            # Trigger focused fix: rewrite only the part that violates assumptions
            final_instruction = (
                f"Your previous solution had the following reflection:\n\n{reflection}\n\n"
                "Please revise your answer to address these concerns explicitly, ensuring all assumptions are valid and all constraints are satisfied."
            )
            final_answer = await self.custom(instruction=final_instruction)
        else:
            # No major flaws found — return refined solution as-is
            final_answer = iterative_solution

        return final_answer
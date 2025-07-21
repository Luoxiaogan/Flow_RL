# Workflow ID: gsm8k_84_1
# Benchmark: gsm8k
# Data Indices: [420, 196]

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
        This is a novel workflow combining Iterative Refinement + Reflect & Regenerate.
        Step 1: Use FlexibleCustom in iterative mode to generate an initial solution with progressive refinement.
        Step 2: Reflect on the final iterative result to identify subtle flaws or missed assumptions.
        Step 3: Based on reflection, use Custom to regenerate a solution that explicitly addresses those points — this is not just a review but a targeted rewrite guided by meta-cognition.
        This avoids ensemble redundancy and instead focuses on deep, structured improvement via iteration + reflection.
        """

        # --- STEP 1: Iterative Refinement using FlexibleCustom ---
        # Run a multi-pass reasoning cycle: initial approach → refine → finalize
        refined_solution = await self.flexible_custom(
            custom_instruction="Begin with a rough estimate and improve through iterative steps.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "verify"],
            max_iterations=3
        )

        # --- STEP 2: Reflection for Meta-Cognitive Critique ---
        reflection_text = await self.reflect(pre_solution=refined_solution)

        # --- STEP 3: Conditional Regeneration Based on Reflection ---
        # If reflection indicates uncertainty or missing steps, prompt for explicit correction
        if "uncertain" in reflection_text.lower() or "assumption" in reflection_text.lower():
            final_answer = await self.custom(
                instruction=f"Given the following reflection:\n\n{reflection_text}\n\nPlease now solve the problem again, focusing on addressing the identified gaps. Be precise, logical, and step-by-step."
            )
        else:
            # If reflection is positive, we can still do one final review pass for polish
            final_answer = await self.review(pre_solution=refined_solution)

        return final_answer
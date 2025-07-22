# Workflow ID: gsm8k_306_1
# Benchmark: gsm8k
# Data Indices: [501, 422, 530]

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
        This is a diverse and complex workflow combining Iterative Refinement + Reflect & Regenerate.
        1. Use FlexibleCustom in iterative mode to generate an initial solution with structured reasoning.
        2. Review the result to improve clarity and logic.
        3. Reflect on the reviewed solution to uncover hidden assumptions or missed steps.
        4. If reflection suggests flaws, regenerate using a targeted instruction based on the reflection.
        5. Otherwise, return the reviewed solution as final.
        
        This design uses iterative refinement (like a loop) and meta-cognitive reflection — a powerful combo that mimics how humans solve hard problems: try, improve, critique, adapt.
        """
        # --- Step 1: Iterative Reasoning via FlexibleCustom ---
        # Start with a multi-step approach (e.g., analyze → plan → solve → verify), iterating once for refinement
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Solve this math problem by breaking it into four phases: first understand what's given, then outline a strategy, execute the calculation, and finally check your work."
        )

        # --- Step 2: Review for Clarity and Logical Flow ---
        refined_solution = await self.review(pre_solution=initial_solution)

        # --- Step 3: Reflect on the Refined Solution ---
        reflection = await self.reflect(pre_solution=refined_solution)

        # --- Step 4: Conditional Regeneration Based on Reflection Content ---
        if "assumption" in reflection.lower() or "missing step" in reflection.lower() or "error" in reflection.lower():
            # If reflection identifies issues, use it to guide a new, focused Custom call
            final_solution = await self.custom(
                instruction=f"Based on the following reflection about the previous solution: '{reflection}'. Now provide a corrected answer, ensuring all steps are logically sound and no assumptions were made beyond the problem statement."
            )
        else:
            # If no major concerns, accept the reviewed solution
            final_solution = refined_solution

        return final_solution
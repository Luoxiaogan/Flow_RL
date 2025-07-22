# Workflow ID: gsm8k_244_1
# Benchmark: gsm8k
# Data Indices: [202, 434]

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
        1. Use FlexibleCustom in iterative mode to generate an initial solution with structured reasoning steps.
        2. If the first iteration fails (e.g., due to ambiguity or error), use Reflect to analyze why.
        3. Then, regenerate using a Custom call informed by reflection — this is a meta-cognitive loop.
        4. Finally, apply one round of Review for polish and clarity.
        
        This logic differs from the existing one by:
        - Using iterative refinement via FlexibleCustom instead of parallel ensemble
        - Introducing conditional logic based on reflection (if no issues found, skip regeneration)
        - Employing a structured, step-wise process that can adapt dynamically
        """
        # --- Step 1: Generate an initial solution using iterative reasoning ---
        flexible_solution = await self.flexible_custom(
            custom_instruction="Use iterative reasoning to solve the problem.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # --- Step 2: Reflect on the result to detect flaws or uncertainty ---
        reflection = await self.reflect(pre_solution=flexible_solution)

        # --- Step 3: Conditional Regeneration Based on Reflection ---
        if "error" in reflection.lower() or "uncertain" in reflection.lower() or "assumption" in reflection.lower():
            final_solution = await self.custom(
                instruction=f"Based on the following reflection: {reflection}. "
                            "Generate a new, improved solution that addresses these concerns."
            )
        else:
            # If reflection indicates no major flaws, just refine with Review
            final_solution = await self.review(pre_solution=flexible_solution)

        return final_solution
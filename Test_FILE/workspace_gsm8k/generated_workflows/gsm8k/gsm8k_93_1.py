# Workflow ID: gsm8k_93_1
# Benchmark: gsm8k
# Data Indices: [118, 653, 710]

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
        Diverse and robust workflow using Parallel Ensemble with a twist: 
        - Generate 3 solutions via FlexibleCustom in parallel mode (each with different reasoning strategies).
        - Use ScEnsemble to select the best one.
        - Apply a final Review step for polishing — not refinement, but clarity and structure.
        
        This is fundamentally different from the existing workflow because:
        1. It uses FlexibleCustom's 'parallel' reasoning pattern directly instead of generating multiple Custom calls manually.
        2. It avoids Reflect + Regenerate entirely — no meta-cognitive loop.
        3. The ensemble step comes before any critique, making it more efficient and less prone to bias from reflection.
        4. Uses a single structured call to FlexibleCustom with parallel steps rather than manual loops.
        """

        # --- PARALLEL ENSEMBLE USING FLEXIBLECUSTOM ---
        # This generates 3 distinct solutions in parallel by applying different reasoning strategies
        parallel_solutions = await self.flexible_custom(
            custom_instruction="Solve this math problem using three different reasoning approaches simultaneously: logical deduction, arithmetic computation, and algebraic modeling.",
            reasoning_pattern="parallel",
            steps=["logical_approach", "arithmetic_approach", "algebraic_approach"],
            use_structured_output=True
        )

        # --- SELECT BEST SOLUTION FROM PARALLEL OUTPUT ---
        # Note: In this case, the output is already a list of solutions due to parallel pattern
        best_solution = await self.sc_ensemble(solutions=parallel_solutions)

        # --- FINAL REVIEW FOR CLARITY AND STRUCTURE ---
        # No rethinking — just polish the final answer for readability and coherence
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
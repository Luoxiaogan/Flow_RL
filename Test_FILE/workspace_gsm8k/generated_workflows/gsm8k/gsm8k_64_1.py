# Workflow ID: gsm8k_64_1
# Benchmark: gsm8k
# Data Indices: [993, 350, 895]

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
        Diverse and complex workflow using the Iterative Refinement pattern as the core logic.
        1. Generate an initial solution with a clear, step-by-step instruction.
        2. Apply Review operator twice to progressively refine it—each time incorporating feedback from the previous iteration.
        3. After refinement, use Reflect to analyze the final solution for potential oversights or assumptions.
        4. If reflection suggests issues, fall back to a new FlexibleCustom call with iterative reasoning to ensure robustness.

        This workflow is fundamentally different from the existing one because:
        - It focuses on iterative improvement via Review (not parallel ensembling or reflection-guided regeneration).
        - Uses a strict sequence of refinement steps (no branching or ensemble selection).
        - Emphasizes progressive enhancement over multiple passes rather than evaluating multiple candidates.
        """
        # --- STEP 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each part clearly and logically."
        )

        # --- STEP 2: Iterative Refinement (Review Twice) ---
        current_solution = initial_solution
        for i in range(2):  # Two rounds of review-based refinement
            current_solution = await self.review(pre_solution=current_solution)

        # --- STEP 3: Final Reflection ---
        final_reflection = await self.reflect(pre_solution=current_solution)

        # --- STEP 4: Conditional Regeneration Based on Reflection ---
        if "error" in final_reflection.lower() or "assumption" in final_reflection.lower():
            # If reflection identifies flaws, start fresh with structured iterative reasoning
            final_answer = await self.flexible_custom(
                custom_instruction="Based on the following reflection, solve the problem again with rigorous, iterative refinement: " + final_reflection,
                reasoning_pattern="iterative",
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=3,
                use_structured_output=True
            )
        else:
            # Otherwise, return the refined solution
            final_answer = current_solution

        return final_answer
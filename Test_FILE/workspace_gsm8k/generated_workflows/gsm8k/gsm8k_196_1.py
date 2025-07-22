# Workflow ID: gsm8k_196_1
# Benchmark: gsm8k
# Data Indices: [690, 9]

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
        This is a diverse workflow combining Iterative Refinement + Reflect-and-Regenerate.
        Step 1: Use FlexibleCustom in iterative mode to generate an initial solution with refinement steps.
        Step 2: Critically reflect on the final refined solution to uncover hidden assumptions or errors.
        Step 3: Based on reflection, regenerate a new solution using a custom instruction that explicitly incorporates the critique — ensuring meta-cognitive improvement.
        Step 4: Finally, review the regenerated answer for clarity and correctness before returning it.

        This design differs from the existing one by:
        - Using iterative refinement (not parallel ensemble) as the core strategy
        - Introducing a reflective critique *before* regeneration, not after selection
        - Ensuring the reflection directly informs a new reasoning path rather than just fixing flaws
        """

        # --- STEP 1: Generate an iteratively refined solution ---
        iterative_solution = await self.flexible_custom(
            custom_instruction="Begin with a rough estimate, then refine step-by-step until confident.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "analyze_assumptions", "refine", "verify"],
            max_iterations=3
        )

        # --- STEP 2: Reflect critically on the iterative result ---
        reflection = await self.reflect(pre_solution=iterative_solution)

        # --- STEP 3: Regenerate a new solution informed by the reflection ---
        improved_solution = await self.custom(
            instruction=f"Using the following reflection on the previous attempt: '{reflection}'. "
                        f"Construct a completely new solution path that avoids the identified pitfalls and leverages better reasoning."
        )

        # --- STEP 4: Review the final improved solution for clarity and logical soundness ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer
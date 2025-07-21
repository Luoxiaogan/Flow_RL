# Workflow ID: gsm8k_73_1
# Benchmark: gsm8k
# Data Indices: [158, 102]

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
        Hybrid workflow combining Reflect-and-Regenerate with Iterative Refinement.
        Step 1: Generate an initial solution using flexible custom (iterative pattern).
        Step 2: Reflect on the solution to uncover hidden assumptions or errors.
        Step 3: Use reflection to guide a targeted refinement via Custom operator.
        Step 4: Final review ensures clarity and correctness.
        This approach combines meta-cognition (Reflect) with progressive improvement (Review/Custom).
        """

        # --- Step 1: Initial Solution via Iterative FlexibleCustom ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Start with an estimate, then refine iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "evaluate", "refine"],
            max_iterations=2
        )

        # --- Step 2: Reflect on the initial solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Regenerate based on reflection ---
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Re-solve the problem carefully, avoiding the issues identified above."
        )

        # --- Step 4: Final polish via Review ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer
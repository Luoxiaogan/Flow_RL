# Workflow ID: gsm8k_106_0
# Benchmark: gsm8k
# Data Indices: [776, 985]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate multiple solutions via parallel ensemble (fan-out).
        2. Select the best solution using ScEnsemble.
        3. Critically reflect on it to uncover hidden assumptions or errors.
        4. Use reflection to guide a new, improved solution (fan-in).
        """
        # --- Step 1: Parallel Ensemble (Fan-out) ---
        solution_candidates = []
        for i in range(3):  # Generate 3 different approaches
            candidate = await self.flexible_custom(
                custom_instruction="Apply a different reasoning strategy each time.",
                reasoning_pattern="sequential",
                steps=["understand", "analyze", "solve", "verify"]
            )
            solution_candidates.append(candidate)

        # --- Step 2: ScEnsemble (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Step 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate Based on Reflection (Reflect-and-Regenerate Pattern) ---
        final_answer = await self.flexible_custom(
            custom_instruction=f"Given the following reflection about the previous solution: '{reflection}'. "
                               f"Re-evaluate the problem with this insight and produce a refined answer.",
            reasoning_pattern="iterative",
            steps=["review_assumptions", "adjust_approach", "recompute", "validate"],
            max_iterations=2
        )

        return final_answer
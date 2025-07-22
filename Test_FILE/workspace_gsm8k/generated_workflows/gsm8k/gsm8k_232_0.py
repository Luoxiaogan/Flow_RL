# Workflow ID: gsm8k_232_0
# Benchmark: gsm8k
# Data Indices: [908, 1]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate multiple solutions via parallel ensemble (robustness).
        Step 2: Select best solution using ScEnsemble.
        Step 3: Reflect on the selected solution to uncover hidden assumptions or errors.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Generate multiple independent solutions (Parallel Ensemble) ---
        solution_candidates = []
        for i in range(3):  # Generate 3 different approaches
            candidate = await self.custom(
                instruction="Solve this math problem by thinking from a different angle each time. "
                           "First, try an algebraic approach. Second, try a step-by-step logical breakdown. "
                           "Third, try estimating first then refining."
            )
            solution_candidates.append(candidate)

        # --- STEP 2: Choose the best among candidates ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- STEP 3: Critically reflect on the chosen solution (meta-cognition) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Use reflection to regenerate a better solution ---
        # We use FlexibleCustom in iterative mode to refine based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection, improve the solution: {reflection}",
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_reasoning", "recompute"],
            max_iterations=2,
            use_structured_output=True
        )

        return refined_solution
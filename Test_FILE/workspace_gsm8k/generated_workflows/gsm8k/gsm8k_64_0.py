# Workflow ID: gsm8k_64_0
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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions (Parallel Ensemble).
        2. Select the best one using ScEnsemble.
        3. Reflect on that solution to identify potential flaws or missed assumptions.
        4. Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Parallel Ensemble ---
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(instruction="Solve the problem step-by-step, explaining each reasoning step clearly.")
            solution_candidates.append(candidate)

        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- STEP 2: Reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 3: Conditional Regeneration Based on Reflection ---
        if "error" in reflection.lower() or "assumption" in reflection.lower():
            # If reflection indicates issues, regenerate using flexible custom with iterative pattern
            improved_solution = await self.flexible_custom(
                custom_instruction="Based on the following reflection, provide an improved solution: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze_assumptions", "correct_errors", "reverify"],
                max_iterations=2,
                use_structured_output=True
            )
        else:
            # If no major flaws found, just refine once using Review
            improved_solution = await self.review(pre_solution=best_solution)

        return improved_solution
# Workflow ID: gsm8k_76_0
# Benchmark: gsm8k
# Data Indices: [624, 778, 642]

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
        Diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on its weaknesses or assumptions.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """

        # --- PARALLEL ENSEMBLE ---
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(instruction="Solve the problem step-by-step, breaking it into clear logical steps. Avoid assumptions unless necessary.")
            solution_candidates.append(candidate)

        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REFLECT ON BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- CONDITIONAL REGENERATION BASED ON REFLECTION ---
        if "assumption" in reflection.lower() or "unclear" in reflection.lower():
            # If reflection indicates uncertainty or flawed logic, use iterative refinement
            refined_solution = await self.flexible_custom(
                custom_instruction="Re-evaluate the problem with attention to potential flaws identified in the reflection.",
                reasoning_pattern="iterative",
                steps=["analyze", "identify_assumptions", "correct_errors", "re-solve"],
                max_iterations=2,
                previous_results=[best_solution]
            )
        else:
            # Otherwise, just improve via review
            refined_solution = await self.review(pre_solution=best_solution)

        return refined_solution
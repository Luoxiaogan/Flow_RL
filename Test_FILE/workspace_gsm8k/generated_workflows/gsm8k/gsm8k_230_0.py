# Workflow ID: gsm8k_230_0
# Benchmark: gsm8k
# Data Indices: [915, 299]

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
        Diverse and effective workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on its weaknesses or assumptions.
        4. Use that reflection to guide a targeted regen with FlexibleCustom in iterative mode.
        """
        # --- Step 1: Parallel Ensemble (Fan-out) ---
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step using a different reasoning approach each time. Focus on clarity and logical structure."
            )
            solution_candidates.append(candidate)

        # --- Step 2: Select Best Candidate ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Step 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Conditional Regeneration Based on Reflection ---
        if "assumption" in reflection.lower() or "unclear" in reflection.lower():
            # If reflection indicates flaws, use FlexibleCustom in iterative mode to refine
            refined_solution = await self.flexible_custom(
                custom_instruction="Based on the following reflection, improve the solution by addressing potential flaws or ambiguities.",
                previous_results=[best_solution, reflection],
                reasoning_pattern="iterative",
                steps=["analyze_reflection", "adjust_reasoning", "recompute"],
                max_iterations=2
            )
            return refined_solution
        else:
            # If no major issues found, just return the best solution
            return best_solution
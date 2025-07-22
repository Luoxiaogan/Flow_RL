# Workflow ID: gsm8k_135_0
# Benchmark: gsm8k
# Data Indices: [779, 570, 772]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on its potential weaknesses or assumptions.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom in iterative mode.
        """
        # --- Step 1: Parallel Ensemble (Fan-out) ---
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Focus on accuracy over speed."
            )
            solution_candidates.append(candidate)

        # --- Step 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Step 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate Based on Reflection (Reflect-and-Regenerate Pattern) ---
        if "assumption" in reflection.lower() or "error" in reflection.lower():
            # If reflection indicates flaws, use FlexibleCustom in iterative mode to refine
            refined_solution = await self.flexible_custom(
                custom_instruction="Improve the solution by addressing the following reflection: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze_assumptions", "correct_errors", "revalidate"],
                max_iterations=2,
                use_structured_output=True
            )
        else:
            # Otherwise, just use the original best solution as final
            refined_solution = best_solution

        return refined_solution
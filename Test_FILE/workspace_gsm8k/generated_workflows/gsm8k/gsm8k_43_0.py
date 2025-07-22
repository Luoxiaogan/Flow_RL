# Workflow ID: gsm8k_43_0
# Benchmark: gsm8k
# Data Indices: [760, 505]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        1. Generate multiple independent solutions (Parallel Ensemble).
        2. Select the best one using ScEnsemble.
        3. Critically reflect on its weaknesses or assumptions (Reflect).
        4. Use that reflection to guide a new, improved solution (FlexibleCustom with iterative pattern).
        """

        # --- Step 1: Generate multiple solutions in parallel ---
        solution_candidates = []
        for _ in range(3):  # Fan-out: generate 3 different approaches
            candidate = await self.custom(
                instruction="Solve the problem by first identifying all known quantities, then applying relevant mathematical operations step-by-step."
            )
            solution_candidates.append(candidate)

        # --- Step 2: Enforce quality control via ensemble ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Step 3: Critical reflection on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Conditional regeneration based on reflection ---
        if "assumption" in reflection.lower() or "error" in reflection.lower():
            # If reflection indicates flaws, use iterative refinement via FlexibleCustom
            refined_solution = await self.flexible_custom(
                custom_instruction="Based on the following reflection, improve the solution: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze_assumptions", "correct_errors", "revalidate"],
                max_iterations=2
            )
            return refined_solution
        else:
            # If no major issues found, just return the best solution
            return best_solution
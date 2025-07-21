# Workflow ID: gsm8k_32_0
# Benchmark: gsm8k
# Data Indices: [632, 730, 164]

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
        1. Generate 3 independent solutions using parallel ensemble.
        2. Select the best solution via ScEnsemble.
        3. Reflect on that solution to uncover potential flaws or improvements.
        4. Use reflection to guide a new, improved solution via FlexibleCustom with iterative pattern.
        """
        # --- Step 1: Parallel Ensemble ---
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step using a clear, logical approach.")
            solutions.append(sol)

        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 2: Reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 3: Conditional regeneration based on reflection ---
        if "error" in reflection.lower() or "assumption" in reflection.lower():
            # If reflection suggests issues, use iterative refinement via FlexibleCustom
            final_solution = await self.flexible_custom(
                custom_instruction="Improve the solution based on this reflection: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze", "refine", "verify"],
                max_iterations=2
            )
        else:
            # Otherwise, use a structured sequential approach to reinforce correctness
            final_solution = await self.flexible_custom(
                custom_instruction="Reconstruct the solution ensuring all steps are logically sound.",
                reasoning_pattern="sequential",
                steps=["identify_knowns", "define_relationships", "solve_stepwise", "validate"]
            )

        return final_solution
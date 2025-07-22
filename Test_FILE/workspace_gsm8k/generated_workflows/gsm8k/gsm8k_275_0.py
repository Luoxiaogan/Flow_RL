# Workflow ID: gsm8k_275_0
# Benchmark: gsm8k
# Data Indices: [332, 831]

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
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect critically on the selected solution to uncover hidden flaws or assumptions.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """

        # --- Step 1: Parallel Ensemble ---
        solutions = []
        for i in range(3):
            instruction = "Solve the problem by breaking it into clear steps. Focus on accuracy over speed."
            sol = await self.custom(instruction=instruction)
            solutions.append(sol)

        # --- Step 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate Based on Reflection (Conditional Logic) ---
        if "error" in reflection.lower() or "assumption" in reflection.lower():
            # If reflection indicates issues, use iterative refinement via FlexibleCustom
            refined_solution = await self.flexible_custom(
                custom_instruction="Based on the following reflection, improve the solution: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze_reflection", "adjust_approach", "recompute"],
                max_iterations=2
            )
            return refined_solution
        else:
            # If no major flaws found, use flexible custom with sequential reasoning
            final_solution = await self.flexible_custom(
                custom_instruction="Now that we have a solid base solution, refine it step-by-step.",
                reasoning_pattern="sequential",
                steps=["verify_knowns", "apply_logic", "check_consistency"]
            )
            return final_solution
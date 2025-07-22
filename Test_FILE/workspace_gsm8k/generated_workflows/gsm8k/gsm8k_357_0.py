# Workflow ID: gsm8k_357_0
# Benchmark: gsm8k
# Data Indices: [622, 533]

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
        Step 3: Reflect on the selected solution to identify potential flaws or missed logic.
        Step 4: Use reflection to guide a new Custom call for final refinement.
        """
        # --- PARALLEL ENSEMBLE ---
        solution_pool = []
        for i in range(3):
            instruction = "Solve the problem step-by-step, breaking it into clear logical parts. Consider multiple approaches if needed."
            sol = await self.custom(instruction=instruction)
            solution_pool.append(sol)

        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- REFLECT AND REGENERATE ---
        reflection = await self.reflect(pre_solution=best_solution)

        # Conditional logic based on reflection content (e.g., if reflection mentions missing steps, use FlexibleCustom)
        if "missing" in reflection.lower() or "assumption" in reflection.lower():
            final_instruction = f"Based on the following reflection:\n{reflection}\nRevise your solution to address these points. Focus on clarity, completeness, and correctness."
            final_answer = await self.flexible_custom(
                custom_instruction=final_instruction,
                reasoning_pattern="sequential",
                steps=["analyze_reflection", "adjust_reasoning", "recompute", "verify"]
            )
        else:
            # If no major issues found, just refine with a simple review
            final_answer = await self.review(pre_solution=best_solution)

        return final_answer
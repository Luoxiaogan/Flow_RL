# Workflow ID: gsm8k_263_0
# Benchmark: gsm8k
# Data Indices: [250, 398]

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
        Diverse and effective workflow combining Parallel Ensemble + Reflect & Regenerate.
        1. Generate 3 independent solutions via parallel ensemble (robustness).
        2. Select the best solution using ScEnsemble.
        3. Reflect on the selected solution to identify potential flaws or missed opportunities.
        4. Use reflection to guide a targeted regen of the solution with FlexibleCustom in iterative mode.
        """
        # --- Step 1: Parallel Ensemble ---
        solution_pool = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve this math problem step-by-step. Focus on clarity and logical structure."
            )
            solution_pool.append(sol)

        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- Step 2: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 3: Conditional Regeneration Based on Reflection ---
        if "incomplete" in reflection.lower() or "assumption" in reflection.lower():
            # If reflection indicates a flaw, regenerate with structured refinement
            final_solution = await self.flexible_custom(
                custom_instruction="Based on the reflection below, refine the solution by addressing gaps or assumptions.",
                previous_results=[best_solution, reflection],
                reasoning_pattern="iterative",
                steps=["analyze_reflection", "correct_assumptions", "re-solve"],
                max_iterations=2
            )
        else:
            # If no major issues found, use the original best solution
            final_solution = best_solution

        return final_solution
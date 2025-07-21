# Workflow ID: gsm8k_189_0
# Benchmark: gsm8k
# Data Indices: [141, 728]

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
        Step 1: Generate multiple independent solutions (Parallel Ensemble).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on it to uncover hidden flaws or assumptions.
        Step 4: Use reflection to guide a new Custom solution for improved accuracy.
        """
        # --- PARALLEL ENSEMBLE ---
        solution_pool = []
        for i in range(3):  # Generate 3 different approaches
            sol = await self.custom(
                instruction="Solve the problem step-by-step. Consider alternative interpretations of ambiguous terms."
            )
            solution_pool.append(sol)

        # --- FAN-IN: Choose the best solution ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- REFLECT AND REGENERATE PATTERN ---
        reflection = await self.reflect(pre_solution=best_solution)

        # Conditional logic based on reflection content (e.g., if it mentions "assumption about X", then refine accordingly)
        if "assumption" in reflection.lower() or "unclear" in reflection.lower():
            final_answer = await self.custom(
                instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a revised solution that addresses these concerns explicitly."
            )
        else:
            # If no major issues found, just return the best solution
            final_answer = best_solution

        return final_answer
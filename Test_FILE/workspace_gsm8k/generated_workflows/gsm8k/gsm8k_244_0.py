# Workflow ID: gsm8k_244_0
# Benchmark: gsm8k
# Data Indices: [202, 434]

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
        2. Select the best solution using ScEnsemble.
        3. Reflect on the selected solution to identify potential flaws or improvements.
        4. Use reflection to guide a new Custom call for final refinement.
        """
        # --- Step 1: Generate multiple solutions in parallel ---
        solutions = []
        for _ in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step, explaining your reasoning clearly."
            )
            solutions.append(solution)

        # --- Step 2: Choose the best solution via ensemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Critically reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate a refined solution based on reflection ---
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        "Now, provide a new, improved solution that addresses the identified issues."
        )

        return final_solution
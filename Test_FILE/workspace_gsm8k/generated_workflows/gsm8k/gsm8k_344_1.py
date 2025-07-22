# Workflow ID: gsm8k_344_1
# Benchmark: gsm8k
# Data Indices: [435, 272]

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
        This is a diverse workflow using Parallel Ensemble with Reflect-guided refinement.
        Step 1: Generate multiple independent solutions (parallel).
        Step 2: Use Reflect to critique the best solution from the ensemble.
        Step 3: Generate one final improved solution based on that reflection.
        This avoids iterative refinement and instead uses parallel exploration + meta-cognitive feedback.
        """
        # --- STEP 1: Generate 3 independent solutions in parallel ---
        solutions = [
            await self.custom(instruction="Solve the problem step-by-step, explaining each reasoning step clearly."),
            await self.custom(instruction="Break the problem into sub-problems and solve them independently. Then combine results."),
            await self.custom(instruction="First identify all knowns and unknowns, then apply relevant formulas or logic.")
        ]

        # --- STEP 2: Select the best solution via ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect critically on the best solution to uncover hidden flaws or assumptions ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Generate a final refined solution informed by the reflection ---
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. Now, provide a new, improved solution that addresses these points."
        )

        return final_solution
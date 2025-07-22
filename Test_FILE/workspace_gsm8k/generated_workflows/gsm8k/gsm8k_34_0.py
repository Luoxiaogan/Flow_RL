# Workflow ID: gsm8k_34_0
# Benchmark: gsm8k
# Data Indices: [628, 290, 160]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best solution using ScEnsemble.
        3. Reflect on its potential flaws or missed assumptions.
        4. Use that reflection to guide a new Custom call for final refinement.
        """

        # --- Step 1: Generate multiple solutions in parallel (Fan-out) ---
        solution_pool = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step by breaking it into logical sub-steps. Avoid assumptions not grounded in the question."
            )
            solution_pool.append(solution)

        # --- Step 2: Evaluate and select the best solution (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- Step 3: Critically reflect on the selected solution (Meta-cognition) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Use reflection to guide a new, improved solution (Regeneration) ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a corrected and more robust solution that addresses any identified weaknesses or gaps."
        )

        return final_answer
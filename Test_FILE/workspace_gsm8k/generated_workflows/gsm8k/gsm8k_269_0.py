# Workflow ID: gsm8k_269_0
# Benchmark: gsm8k
# Data Indices: [975, 279]

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
        Step 1: Generate 3 independent solutions using parallel reasoning (Fan-out).
        Step 2: Select the best one via ScEnsemble.
        Step 3: Reflect on its potential flaws or assumptions.
        Step 4: Use that reflection to guide a new, improved solution (Regenerate).
        """
        # --- PARALLEL ENSEMBLE: Generate multiple initial approaches ---
        solution_pool = []
        for i in range(3):
            instruction = f"Approach the problem from a different perspective: {['algebraic', 'conceptual', 'step-by-step'][i]}"
            sol = await self.custom(instruction=instruction)
            solution_pool.append(sol)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- REFLECT ON THE BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE WITH REFLECTION GUIDANCE ---
        final_instruction = (
            "Given the following reflection on the previous solution:\n"
            f"{reflection}\n\n"
            "Now, synthesize this insight into a completely new, improved solution. "
            "Ensure clarity, logical flow, and correctness."
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution
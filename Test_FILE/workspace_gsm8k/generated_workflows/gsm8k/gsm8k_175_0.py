# Workflow ID: gsm8k_175_0
# Benchmark: gsm8k
# Data Indices: [602, 465]

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
        Step 1: Generate 3 independent solutions (Parallel Ensemble).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on it to identify potential flaws or improvements.
        Step 4: Use reflection to guide a new, targeted Custom call for final refinement.
        """

        # --- PARALLEL ENSEMBLE: Generate multiple initial solutions ---
        solution_pool = []
        for _ in range(3):
            solution = await self.custom(
                instruction="Solve the problem by breaking it into logical steps. Think step-by-step."
            )
            solution_pool.append(solution)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- REFLECT ON THE BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE BASED ON REFLECTION ---
        final_instruction = (
            "Given the following reflection on the initial solution:\n"
            f"{reflection}\n\n"
            "Now, produce a refined and improved answer that addresses these points."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer
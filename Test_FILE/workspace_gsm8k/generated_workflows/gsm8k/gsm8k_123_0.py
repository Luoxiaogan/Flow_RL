# Workflow ID: gsm8k_123_0
# Benchmark: gsm8k
# Data Indices: [5, 41]

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
        2. Select the best one using ScEnsemble.
        3. Reflect on that solution to identify potential flaws or improvements.
        4. Use the reflection to guide a new Custom call for a refined final answer.
        """
        # --- Step 1: Parallel Ensemble ---
        solution_list = []
        for i in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")
            solution_list.append(sol)
        
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 2: Reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 3: Regenerate based on reflection ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses the identified issues."
        )

        return final_answer
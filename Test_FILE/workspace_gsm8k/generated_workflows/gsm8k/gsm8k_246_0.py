# Workflow ID: gsm8k_246_0
# Benchmark: gsm8k
# Data Indices: [304, 675, 939]

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
        Step 1: Generate 3 independent solutions via parallel ensemble (robustness).
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on that solution to uncover potential blind spots or assumptions.
        Step 4: Use the reflection to guide a new Custom call for an improved final answer.
        """

        # --- STEP 1: Generate multiple candidate solutions in parallel ---
        solutions = []
        for i in range(3):
            sol = await self.custom(instruction="Solve this math problem step-by-step. Consider all possible interpretations of the question.")
            solutions.append(sol)

        # --- STEP 2: Pick the best one using ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect critically on the chosen solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate a refined solution based on reflection ---
        final_answer = await self.custom(
            instruction=f"Given the following initial solution and reflection, improve it:\n\nInitial Solution:\n{best_solution}\n\nReflection:\n{reflection}\n\nProvide a final, accurate answer."
        )

        return final_answer
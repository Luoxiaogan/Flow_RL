# Workflow ID: gsm8k_182_0
# Benchmark: gsm8k
# Data Indices: [86, 152, 589]

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
        1. Generate 3 independent solutions via parallel ensemble (fan-out).
        2. Select the best solution using ScEnsemble.
        3. Reflect critically on that best solution to identify potential blind spots or assumptions.
        4. Use the reflection to guide a new Custom call for an improved final answer.
        """
        # Step 1: Generate multiple solutions in parallel (Fan-out)
        solution_pool = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, showing all calculations clearly.")
            solution_pool.append(sol)

        # Step 2: Evaluate and select the best one (Fan-in)
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect on the best solution to uncover hidden flaws or missed logic
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a refined solution based on reflection (Reflect-and-Regenerate pattern)
        final_instruction = f"Given the following initial solution:\n{best_solution}\n\nAnd this reflection on its weaknesses or assumptions:\n{reflection}\n\nNow, provide a fully revised and improved solution that addresses these points."
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer
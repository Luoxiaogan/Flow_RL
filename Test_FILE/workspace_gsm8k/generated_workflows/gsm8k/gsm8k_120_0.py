# Workflow ID: gsm8k_120_0
# Benchmark: gsm8k
# Data Indices: [674, 9, 953]

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
        3. Reflect on its potential flaws or missed steps.
        4. Use that reflection to guide a new Custom call for a refined answer.
        """
        # Step 1: Generate multiple initial solutions (Parallel Ensemble pattern)
        solutions = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve this math problem step-by-step, breaking it into clear logical parts."
            )
            solutions.append(solution)

        # Step 2: Choose the best one using ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the chosen solution (Reflect operator)
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate with guidance from reflection (Reflect-and-Regenerate pattern)
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the previous solution: '{reflection}'. "
                        f"Re-solve the problem with improved clarity, addressing any overlooked assumptions or gaps. "
                        f"Provide a complete, logically sound explanation."
        )

        return final_answer
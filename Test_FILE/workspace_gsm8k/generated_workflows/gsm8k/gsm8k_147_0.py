# Workflow ID: gsm8k_147_0
# Benchmark: gsm8k
# Data Indices: [372, 264, 429]

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
        This is a diverse and efficient workflow using iterative refinement with reflection.
        It uses the Reflect operator to guide a targeted improvement, avoiding unnecessary complexity.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down each part logically."
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws or missing steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution that addresses the critique
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. Now, provide a revised, improved solution that addresses these points."
        )

        return final_solution
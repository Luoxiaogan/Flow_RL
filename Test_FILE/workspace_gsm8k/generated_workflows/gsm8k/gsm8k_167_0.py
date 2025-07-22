# Workflow ID: gsm8k_167_0
# Benchmark: gsm8k
# Data Indices: [485, 397, 940]

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
        This is a diverse and efficient workflow using Reflect + Custom to guide iterative improvement.
        It avoids unnecessary complexity while ensuring logical reasoning through meta-cognition.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(instruction="Solve the problem by breaking it down into smaller steps. Explain each step clearly.")

        # Step 2: Reflect on the initial solution to identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        "Now, provide a new, improved solution that addresses these points."
        )

        return final_solution
# Workflow ID: gsm8k_122_0
# Benchmark: gsm8k
# Data Indices: [766, 449, 307]

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
        This is a diverse and efficient workflow using the Reflect-and-Regenerate pattern.
        It generates an initial solution, reflects on it to identify potential flaws or improvements,
        then uses that reflection to guide a refined solution. This mimics human meta-cognition
        while remaining simple and effective — only 3 steps total.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each calculation clearly."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a better solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        "Now, provide a new, improved solution that addresses any identified issues."
        )

        return final_solution
# Workflow ID: gsm8k_75_0
# Benchmark: gsm8k
# Data Indices: [756, 204]

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
        This is a diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, critically reflects on it, then uses that reflection
        to guide a refined solution — mimicking human meta-cognition for improved accuracy.
        """
        # Step 1: Generate an initial solution using general reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step by identifying knowns, unknowns, and relationships between variables."
        )

        # Step 2: Reflect critically on the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a better solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        "Now, provide a new, improved solution with clearer logic and no assumptions that might be flawed."
        )

        return final_solution
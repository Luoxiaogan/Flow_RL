# Workflow ID: gsm8k_383_0
# Benchmark: gsm8k
# Data Indices: [563, 733, 360]

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
        It generates an initial solution, reflects on it to uncover potential flaws or missed steps,
        then uses that reflection to guide a refined solution — all in just 3 steps.
        """
        # Step 1: Generate initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution to identify assumptions, gaps, or errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a more robust and accurate final answer
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        "Now, provide a new, improved solution that addresses any issues identified above."
        )

        return final_solution
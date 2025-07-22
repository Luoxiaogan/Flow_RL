# Workflow ID: gsm8k_153_0
# Benchmark: gsm8k
# Data Indices: [794, 411]

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
        It generates an initial solution, reflects on it to identify potential blind spots,
        then uses that reflection to guide a refined solution — all in under 5 steps.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into clear, logical steps. Explain each step explicitly."
        )

        # Step 2: Critically reflect on the solution to uncover assumptions or gaps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a targeted, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity and accuracy."
        )

        return final_solution
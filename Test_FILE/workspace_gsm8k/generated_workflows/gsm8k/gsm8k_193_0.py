# Workflow ID: gsm8k_193_0
# Benchmark: gsm8k
# Data Indices: [107, 981, 266]

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
        This is a diverse and efficient workflow using the Reflect + Custom pattern.
        It generates an initial solution, reflects on it to uncover potential blind spots,
        then uses that reflection to guide a targeted improvement — all in under 5 steps.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into logical steps. First identify what's given, then determine what needs to be calculated, and finally compute the result."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again, ensuring any overlooked assumptions or errors are addressed."
        )

        return final_solution
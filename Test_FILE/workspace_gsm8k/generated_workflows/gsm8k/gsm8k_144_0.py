# Workflow ID: gsm8k_144_0
# Benchmark: gsm8k
# Data Indices: [219, 151, 137]

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
        Diverse and efficient workflow using Reflect + Custom to guide a targeted improvement.
        This avoids unnecessary loops or ensembles while still leveraging meta-cognition for quality.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(instruction="Solve the problem by breaking it down into smaller steps. Explain each step clearly.")

        # Step 2: Reflect on the solution — identify potential flaws, missing assumptions, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        "Now, provide a revised solution that addresses these points and ensures accuracy."
        )

        return final_solution
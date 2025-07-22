# Workflow ID: gsm8k_305_0
# Benchmark: gsm8k
# Data Indices: [115, 817, 70]

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
        Efficient and diverse workflow using Reflect + Custom to guide a targeted improvement.
        This avoids unnecessary complexity while ensuring logical reasoning and meta-cognition.
        """
        # Step 1: Generate an initial solution with clear step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller steps. First identify what is given, then determine what needs to be calculated, and finally perform the arithmetic accurately."
        )

        # Step 2: Critically reflect on the solution — look for missing steps, errors, or unclear logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution that addresses potential flaws
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. Now, provide a corrected and improved solution that explicitly addresses any issues identified."
        )

        return final_solution
# Workflow ID: gsm8k_51_0
# Benchmark: gsm8k
# Data Indices: [325, 528]

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
        It leverages the Reflect operator to guide a targeted improvement, avoiding unnecessary complexity.
        """
        # Step 1: Generate an initial solution using a flexible custom operator in sequential mode
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem logically and solve step-by-step."
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution via Custom
        final_solution = await self.custom(
            instruction=f"Based on the following reflection:\n{reflection}\n\nProvide a revised, accurate solution."
        )

        return final_solution
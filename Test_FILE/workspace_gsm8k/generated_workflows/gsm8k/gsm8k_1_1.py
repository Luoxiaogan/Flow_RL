# Workflow ID: gsm8k_1_1
# Benchmark: gsm8k
# Data Indices: [4, 2]

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
        This workflow follows the 'Reflect and Regenerate' pattern.
        It first generates a solution, reflects on it, and then uses that reflection to generate a more refined solution.
        """

        # Step 1: Generate an initial solution using a flexible custom reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into logical steps",
            reasoning_pattern="sequential",
            steps=["identify", "analyze", "solve", "verify"]
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, more refined solution
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}', provide a more accurate and detailed solution."
        )

        return refined_solution
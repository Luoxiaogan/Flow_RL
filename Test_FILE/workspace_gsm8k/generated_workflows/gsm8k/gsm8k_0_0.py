# Workflow ID: gsm8k_0_0
# Benchmark: gsm8k
# Data Indices: [1, 6]

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
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Break the problem into logical steps and solve systematically",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a more refined solution
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Now, provide a more accurate and detailed solution."
        )

        # Step 4: Review the improved solution to ensure clarity and correctness
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution
# Workflow ID: gsm8k_237_1
# Benchmark: gsm8k
# Data Indices: [257, 146]

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
        It generates an initial solution, reflects on it to identify potential flaws or missed steps,
        then uses that reflection to guide a targeted refinement — all in just 3 steps.
        This avoids unnecessary parallelism or multiple reviews, focusing instead on meta-cognitive improvement.
        """

        # Step 1: Generate initial solution with clear step-by-step instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each calculation clearly."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a focused, improved solution
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, provide a revised solution that addresses these points while maintaining clarity and correctness."
        )

        return final_answer
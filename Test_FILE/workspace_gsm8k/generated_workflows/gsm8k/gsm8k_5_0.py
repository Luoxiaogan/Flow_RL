# Workflow ID: gsm8k_5_0
# Benchmark: gsm8k
# Data Indices: [248, 657, 313]

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
        It generates an initial solution, reflects on it to uncover blind spots, then uses that reflection
        to guide a targeted refinement — all in under 5 steps.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break down the math clearly, showing each operation."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a focused, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial approach: '{reflection}'. "
                        f"Re-solve the problem by addressing the identified concerns, ensuring clarity and correctness."
        )

        return final_solution
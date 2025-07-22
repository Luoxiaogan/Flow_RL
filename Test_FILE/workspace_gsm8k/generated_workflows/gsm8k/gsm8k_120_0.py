# Workflow ID: gsm8k_120_0
# Benchmark: gsm8k
# Data Indices: [906, 125]

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
        It generates an initial solution, reflects on its potential flaws, then uses that reflection
        to guide a targeted re-solution — minimizing unnecessary steps while maximizing insight.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining each calculation clearly.")

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a focused, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a refined and accurate solution."
        )

        return final_solution
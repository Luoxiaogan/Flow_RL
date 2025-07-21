# Workflow ID: gsm8k_157_0
# Benchmark: gsm8k
# Data Indices: [28, 543, 877]

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
        Diverse and efficient workflow using Reflect + Custom to guide a targeted refinement.
        This mimics meta-cognition: solve → reflect → improve — without unnecessary complexity.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining each calculation clearly.")

        # Step 2: Critically reflect on the solution to identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a focused revision — this is more efficient than blind review
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, re-solve the problem carefully, ensuring all steps are logically sound and mathematically correct."
        )

        return final_solution
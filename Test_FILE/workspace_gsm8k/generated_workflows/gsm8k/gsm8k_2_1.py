# Workflow ID: gsm8k_2_1
# Benchmark: gsm8k
# Data Indices: [355, 791, 991]

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
        Reflect and Regenerate Workflow: Generate an initial solution, reflect on its weaknesses, then use that reflection to guide a targeted revision.
        This meta-cognitive approach improves accuracy by explicitly identifying and addressing potential flaws in reasoning.
        """
        # Step 1: Generate an initial solution with clear step-by-step logic
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Explain each step clearly."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or possible errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses these points."
        )

        return final_solution
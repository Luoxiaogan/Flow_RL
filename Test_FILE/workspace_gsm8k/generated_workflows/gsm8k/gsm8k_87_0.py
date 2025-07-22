# Workflow ID: gsm8k_87_0
# Benchmark: gsm8k
# Data Indices: [122, 708]

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
        This is a diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        It generates an initial solution, critically reflects on it, then uses that reflection
        to guide a new, improved solution — mimicking meta-cognitive reasoning.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Be explicit about each calculation."
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws or missed assumptions
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to guide a fresh attempt at solving the problem
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses these points."
        )

        return final_solution
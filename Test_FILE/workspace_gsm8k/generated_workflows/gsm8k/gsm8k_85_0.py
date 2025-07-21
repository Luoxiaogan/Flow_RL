# Workflow ID: gsm8k_85_0
# Benchmark: gsm8k
# Data Indices: [242, 952]

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
        It first generates an initial solution, critically reflects on it, then uses that reflection
        to guide a refined, higher-quality final solution.
        """
        # Step 1: Generate an initial solution with step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller steps. Be explicit about each calculation."
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws or missed opportunities
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        "Now, re-solve the problem with this insight in mind. Ensure clarity, accuracy, and completeness."
        )

        return final_solution
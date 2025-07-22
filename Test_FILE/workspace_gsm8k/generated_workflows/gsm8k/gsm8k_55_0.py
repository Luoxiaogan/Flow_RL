# Workflow ID: gsm8k_55_0
# Benchmark: gsm8k
# Data Indices: [782, 557]

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
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to produce a superior, improved solution.
        """
        # Step 1: Generate an initial solution with general step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller steps. Explain each step clearly."
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws, assumptions, or missed opportunities
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted Custom call for an improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                        "Now, provide a refined, more accurate, and logically sound solution."
        )

        return final_solution
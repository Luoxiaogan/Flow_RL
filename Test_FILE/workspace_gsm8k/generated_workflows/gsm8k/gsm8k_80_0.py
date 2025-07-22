# Workflow ID: gsm8k_80_0
# Benchmark: gsm8k
# Data Indices: [225, 238]

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
        This is a diverse and reflective workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to guide a new, improved solution.
        """
        # Step 1: Generate an initial solution with general reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution — identify potential flaws or missed aspects
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to guide a new, more thoughtful solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Now, provide a new, improved solution. Be especially careful about assumptions, logical gaps, and clarity."
        )

        return final_solution
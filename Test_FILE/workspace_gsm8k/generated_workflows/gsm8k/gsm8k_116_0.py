# Workflow ID: gsm8k_116_0
# Benchmark: gsm8k
# Data Indices: [491, 348]

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
        and finally uses that reflection to guide a refined solution — mimicking meta-cognitive reasoning.
        """
        # Step 1: Generate an initial solution with general step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into clear, logical steps. Show all calculations explicitly."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to generate a superior, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                        "Now, provide a new, more accurate, and better-structured solution based on this insight."
        )

        return final_solution
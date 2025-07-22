# Workflow ID: gsm8k_376_1
# Benchmark: gsm8k
# Data Indices: [427, 369]

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
        Diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        This approach first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to guide a new, improved solution — mimicking meta-cognitive reasoning.
        This is fundamentally different from iterative refinement: instead of fixing step-by-step,
        it evaluates *why* the solution might be flawed and rebuilds accordingly.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, potential errors, or missed perspectives
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a fresh, targeted solution attempt
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        "Now, provide a revised solution that addresses these points explicitly."
        )

        return final_solution
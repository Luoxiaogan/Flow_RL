# Workflow ID: gsm8k_31_0
# Benchmark: gsm8k
# Data Indices: [396, 926, 650]

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
        to guide a more refined solution. This mimics meta-cognitive reasoning for improved accuracy.
        """

        # Step 1: Generate an initial solution using a general-purpose custom instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws, assumptions, or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Now, provide a new, improved solution that addresses the identified issues."
        )

        return final_solution
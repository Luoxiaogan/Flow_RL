# Workflow ID: gsm8k_59_0
# Benchmark: gsm8k
# Data Indices: [615, 522, 142]

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
        This is a diverse and efficient workflow using the Reflect + Custom pattern.
        It generates an initial solution, reflects on it to uncover potential blind spots,
        then uses that reflection to guide a refined solution — all in under 5 steps.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what is given. Then, determine what needs to be calculated. Finally, compute the answer clearly."
        )

        # Step 2: Critically reflect on the initial solution for flaws or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following initial solution:\n{initial_solution}\n\nAnd this reflection on possible weaknesses or oversights:\n{reflection}\n\nNow provide a revised, more accurate solution."
        )

        return final_solution
# Workflow ID: gsm8k_121_0
# Benchmark: gsm8k
# Data Indices: [795, 755, 981]

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
        Iterative Refinement Workflow: Generate an initial solution, then improve it through two rounds of review.
        This pattern ensures gradual enhancement by identifying and correcting errors or omissions in each iteration.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Do not skip any steps."
        )

        # Step 2: First refinement - Review to identify flaws and improve clarity
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement - Review again to catch subtler issues
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
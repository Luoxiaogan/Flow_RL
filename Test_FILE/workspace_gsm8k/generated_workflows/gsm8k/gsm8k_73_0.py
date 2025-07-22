# Workflow ID: gsm8k_73_0
# Benchmark: gsm8k
# Data Indices: [2, 699, 254]

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
        Iterative Refinement Workflow: Generate an initial solution and improve it through two rounds of review.
        This pattern ensures gradual enhancement by identifying and fixing flaws in successive iterations.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, clearly explaining each reasoning step."
        )

        # Step 2: First refinement - use Review to improve the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement - apply another round of Review for deeper improvement
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
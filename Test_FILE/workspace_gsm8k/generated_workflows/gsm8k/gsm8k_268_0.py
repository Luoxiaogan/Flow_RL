# Workflow ID: gsm8k_268_0
# Benchmark: gsm8k
# Data Indices: [718, 25]

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
        Iterative Refinement Workflow: Generate an initial solution and refine it twice using Review.
        This pattern ensures progressive improvement through structured critique and revision.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down the problem into logical components."
        )

        # Step 2: First refinement — improve based on internal review
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further enhance the already improved solution
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
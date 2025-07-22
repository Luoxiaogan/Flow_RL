# Workflow ID: gsm8k_33_0
# Benchmark: gsm8k
# Data Indices: [749, 960, 552]

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
        Iterative Refinement Workflow: Generate an initial solution, then refine it twice using Review.
        This pattern ensures gradual improvement by addressing errors or omissions in each iteration.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down the problem into logical parts."
        )

        # Step 2: First refinement - improve clarity, correctness, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement - address any remaining issues from the first review
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
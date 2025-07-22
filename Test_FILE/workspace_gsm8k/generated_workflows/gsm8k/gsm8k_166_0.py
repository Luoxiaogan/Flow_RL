# Workflow ID: gsm8k_166_0
# Benchmark: gsm8k
# Data Indices: [168, 660, 851]

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
        This pattern ensures progressive improvement through structured critique and revision.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break down the problem into logical parts, define variables, and show all calculations."
        )

        # Step 2: First refinement — review the initial solution for clarity, correctness, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply another round of review to catch any remaining issues
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
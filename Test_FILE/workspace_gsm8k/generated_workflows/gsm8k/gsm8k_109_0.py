# Workflow ID: gsm8k_109_0
# Benchmark: gsm8k
# Data Indices: [526, 87]

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
        This pattern ensures progressive improvement through structured critique.
        """
        # Step 1: Generate an initial solution with step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into clear, logical steps. Explain each step thoroughly."
        )

        # Step 2: First refinement — review the initial solution for clarity and accuracy
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply another round of review to catch any remaining issues
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
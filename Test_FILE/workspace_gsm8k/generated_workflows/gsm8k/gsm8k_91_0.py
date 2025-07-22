# Workflow ID: gsm8k_91_0
# Benchmark: gsm8k
# Data Indices: [773, 854]

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
        This pattern ensures progressive enhancement by identifying weaknesses and addressing them step-by-step.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin solving the problem using clear, step-by-step reasoning.",
            reasoning_pattern="sequential",
            steps=["understand", "break_down", "solve", "verify"]
        )

        # Step 2: First refinement pass — critique and rewrite the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — further improve based on the first revision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
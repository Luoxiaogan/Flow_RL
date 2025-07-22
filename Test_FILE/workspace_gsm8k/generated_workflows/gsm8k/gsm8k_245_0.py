# Workflow ID: gsm8k_245_0
# Benchmark: gsm8k
# Data Indices: [596, 71]

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
        This pattern ensures progressive improvement by identifying and correcting flaws in each iteration.
        """
        # Step 1: Generate an initial solution using a structured reasoning approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin with a clear step-by-step breakdown of the problem.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # Step 2: First refinement — review the initial solution for clarity, accuracy, and logic flow
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further improve based on the first review
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
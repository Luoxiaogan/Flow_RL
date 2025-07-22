# Workflow ID: gsm8k_316_0
# Benchmark: gsm8k
# Data Indices: [447, 83]

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
        This pattern ensures logical progression and iterative enhancement without relying on ensembling or reflection.
        """
        # Step 1: Generate a simple, direct solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear reasoning.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: First refinement — critique and improve the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further enhance the already improved solution
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
# Workflow ID: gsm8k_147_0
# Benchmark: gsm8k
# Data Indices: [270, 991]

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
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and solve systematically.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: First refinement — review the initial solution to improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply another round of review for deeper improvements
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
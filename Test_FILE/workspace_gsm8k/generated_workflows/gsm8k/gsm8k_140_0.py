# Workflow ID: gsm8k_140_0
# Benchmark: gsm8k
# Data Indices: [169, 228]

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
        This pattern ensures logical progression and improved accuracy through structured critique.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: First refinement pass — improve the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — further enhance based on the first revision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
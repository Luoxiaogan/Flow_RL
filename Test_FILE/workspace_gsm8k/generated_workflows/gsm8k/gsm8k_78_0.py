# Workflow ID: gsm8k_78_0
# Benchmark: gsm8k
# Data Indices: [793, 571]

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
        This pattern ensures progressive enhancement by leveraging structured feedback loops.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break the problem into smaller parts and solve step-by-step."
        )

        # Step 2: First refinement via Review — critique and improve the initial attempt
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review — further polish based on the first revision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
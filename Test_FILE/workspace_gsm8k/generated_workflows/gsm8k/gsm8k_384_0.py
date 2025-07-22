# Workflow ID: gsm8k_384_0
# Benchmark: gsm8k
# Data Indices: [972, 922]

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
        This pattern ensures logical progression and improved accuracy through successive feedback loops.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"],
            custom_instruction="Break the problem into clear steps and solve each logically."
        )

        # Step 2: First refinement pass — review the initial solution to improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — further improve based on the first review
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
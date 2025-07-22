# Workflow ID: gsm8k_30_0
# Benchmark: gsm8k
# Data Indices: [863, 90]

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
        This pattern ensures progressive improvement through structured feedback loops.
        """
        # Step 1: Generate a simple initial solution using FlexibleCustom in sequential mode
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and solve it clearly.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # Step 2: First refinement pass — improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — address any remaining ambiguities or errors
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
# Workflow ID: gsm8k_283_0
# Benchmark: gsm8k
# Data Indices: [943, 810, 448]

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
        This pattern ensures progressive improvement by focusing on clarity, correctness, and completeness.
        """
        # Step 1: Generate a simple initial solution using a general instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: First refinement — improve clarity and logical flow
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — ensure all steps are mathematically sound and no assumptions are missed
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
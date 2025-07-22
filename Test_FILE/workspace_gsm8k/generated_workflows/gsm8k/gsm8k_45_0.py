# Workflow ID: gsm8k_45_0
# Benchmark: gsm8k
# Data Indices: [491, 441]

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
        This pattern ensures progressive improvement by identifying and correcting flaws in each pass.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify all given quantities. Then, apply relevant operations in order. Finally, state the final answer clearly."
        )

        # Step 2: First refinement - improve clarity, logic flow, and accuracy
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement - focus on potential errors, missing steps, or ambiguous language
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
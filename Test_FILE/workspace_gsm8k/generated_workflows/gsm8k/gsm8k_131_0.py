# Workflow ID: gsm8k_131_0
# Benchmark: gsm8k
# Data Indices: [30, 984, 930]

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
        This pattern ensures progressive improvement by identifying and correcting errors in each iteration.
        """
        # Step 1: Generate initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what is given. Then, determine what needs to be found. Finally, calculate the answer logically."
        )

        # Step 2: First refinement - improve clarity, structure, and logic flow
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement - check for numerical accuracy, missing steps, or conceptual gaps
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
# Workflow ID: gsm8k_207_0
# Benchmark: gsm8k
# Data Indices: [392, 803]

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
        This pattern ensures progressive improvement through critical feedback loops.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Show your work clearly."
        )

        # Step 2: First refinement — review and improve the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply another round of review for deeper accuracy
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
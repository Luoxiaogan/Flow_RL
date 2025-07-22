# Workflow ID: gsm8k_188_0
# Benchmark: gsm8k
# Data Indices: [655, 750]

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
        This pattern ensures logical progression from a rough draft to a polished answer.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First identify what is being asked, then list known quantities, and finally compute the result."
        )

        # Step 2: Apply iterative refinement using Review operator twice
        # Each review improves clarity, accuracy, or structure of the prior solution
        first_refinement = await self.review(pre_solution=initial_solution)
        second_refinement = await self.review(pre_solution=first_refinement)

        return second_refinement
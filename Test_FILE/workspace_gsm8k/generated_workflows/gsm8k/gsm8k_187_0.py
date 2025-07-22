# Workflow ID: gsm8k_187_0
# Benchmark: gsm8k
# Data Indices: [195, 502]

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
        This pattern ensures gradual improvement by progressively addressing weaknesses in the reasoning.
        """
        # Step 1: Generate a basic solution with clear step-by-step breakdown
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what is given. Then, determine what needs to be found. Finally, perform the necessary calculations."
        )

        # Step 2: Apply iterative refinement — review once to improve clarity and logic
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Review again to catch any subtle errors or missing assumptions
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
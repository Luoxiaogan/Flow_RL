# Workflow ID: gsm8k_303_0
# Benchmark: gsm8k
# Data Indices: [576, 193, 342]

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
        This pattern ensures progressive improvement by addressing potential oversights in each iteration.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into logical parts and explain each step clearly."
        )

        # Step 2: First refinement - improve clarity, structure, and correctness
        first_refinement = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement - focus on completeness, edge cases, and deeper analysis
        second_refinement = await self.review(pre_solution=first_refinement)

        return second_refinement
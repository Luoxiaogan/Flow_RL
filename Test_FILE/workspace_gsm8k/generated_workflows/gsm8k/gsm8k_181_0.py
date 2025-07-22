# Workflow ID: gsm8k_181_0
# Benchmark: gsm8k
# Data Indices: [765, 126]

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
        This structure ensures progressive improvement through critical feedback loops.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: First refinement — improve based on internal critique
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further polish the solution
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        return refined_solution_2
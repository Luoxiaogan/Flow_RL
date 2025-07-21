# Workflow ID: gsm8k_118_0
# Benchmark: gsm8k
# Data Indices: [335, 601, 387]

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
        This pattern ensures progressive improvement by systematically addressing weaknesses in each step.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into logical parts and explain each step clearly."
        )

        # Step 2: First refinement pass — improve clarity, logic flow, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — address subtle errors or assumptions missed earlier
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
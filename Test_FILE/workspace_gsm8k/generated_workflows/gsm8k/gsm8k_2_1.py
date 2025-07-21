# Workflow ID: gsm8k_2_1
# Benchmark: gsm8k
# Data Indices: [3, 0]

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
        This workflow uses the 'Iterative Refinement' pattern.
        It starts with a basic solution, then applies the Review operator twice to refine it.
        """

        # Step 1: Generate an initial solution using a general reasoning approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Break the problem into logical steps and solve step-by-step.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: First review to improve the initial solution
        first_review = await self.review(pre_solution=initial_solution)

        # Step 3: Second review to further refine the solution
        second_review = await self.review(pre_solution=first_review)

        return second_review
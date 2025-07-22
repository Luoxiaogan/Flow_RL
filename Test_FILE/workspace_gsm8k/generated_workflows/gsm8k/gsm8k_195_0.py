# Workflow ID: gsm8k_195_0
# Benchmark: gsm8k
# Data Indices: [709, 46, 761]

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
        This pattern ensures gradual improvement through focused critique and revision.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "formulate_equation", "solve", "verify"],
            custom_instruction="Break the problem into clear logical steps and solve systematically."
        )

        # Step 2: First refinement – improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement – enhance rigor and completeness
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
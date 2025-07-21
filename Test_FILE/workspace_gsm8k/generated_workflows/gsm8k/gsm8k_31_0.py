# Workflow ID: gsm8k_31_0
# Benchmark: gsm8k
# Data Indices: [192, 984, 756]

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
        This pattern ensures progressive improvement through structured critique.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying the key elements of the problem and solving step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify"]
        )

        # Step 2: First refinement — improve the initial solution via review
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further enhance the solution
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
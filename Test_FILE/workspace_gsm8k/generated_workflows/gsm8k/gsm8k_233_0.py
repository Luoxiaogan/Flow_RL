# Workflow ID: gsm8k_233_0
# Benchmark: gsm8k
# Data Indices: [590, 429]

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
        # Step 1: Generate an initial solution using a structured reasoning approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying the key variables and relationships in the problem.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_equations", "solve", "verify"]
        )

        # Step 2: First refinement — review to improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further enhance based on the first revision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
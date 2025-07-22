# Workflow ID: gsm8k_164_0
# Benchmark: gsm8k
# Data Indices: [453, 813, 546]

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
        Iterative Refinement Workflow: Generate an initial solution, then improve it through two rounds of review.
        This pattern ensures progressive enhancement by systematically identifying and correcting flaws.
        """
        # Step 1: Generate a baseline solution using general reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Be concise but thorough."
        )

        # Step 2: First refinement — critique and rewrite for clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further improve based on deeper analysis
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
# Workflow ID: gsm8k_12_0
# Benchmark: gsm8k
# Data Indices: [558, 286, 390]

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
        This pattern ensures logical progression and error correction without overcomplicating the structure.
        """
        # Step 1: Generate a clear, step-by-step initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Be explicit about each calculation."
        )

        # Step 2: First refinement — critique and rewrite for clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further improve based on deeper scrutiny
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
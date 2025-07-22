# Workflow ID: gsm8k_367_0
# Benchmark: gsm8k
# Data Indices: [556, 220, 839]

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
        Iterative Refinement Workflow: Generate an initial solution and improve it through two rounds of review.
        This pattern ensures logical progression from a rough draft to a polished answer.
        """
        # Step 1: Generate an initial solution using a general-purpose custom instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each reasoning step clearly. Do not skip any details."
        )

        # Step 2: First refinement — use Review to enhance clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply another round of Review for deeper improvements
        second_refined = await self.review(pre_solution=first_refined)

        # Optional: Use Reflect to critique the final version (can be used in future iterations)
        reflection = await self.reflect(pre_solution=second_refined)

        # Final Output: Return the most refined solution
        return second_refined
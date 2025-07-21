# Workflow ID: gsm8k_160_1
# Benchmark: gsm8k
# Data Indices: [928, 278, 715]

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
        This is a diverse and efficient workflow using the Iterative Refinement pattern.
        It generates an initial solution, then progressively improves it through two rounds of review.
        This approach ensures robustness by catching subtle errors and enhancing clarity step-by-step.
        """
        # Step 1: Generate a basic solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Show all calculations explicitly."
        )

        # Step 2: First refinement — improve clarity and correctness
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — ensure logical consistency and completeness
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        return refined_solution_2
# Workflow ID: gsm8k_319_1
# Benchmark: gsm8k
# Data Indices: [703, 616, 412]

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
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern.
        It starts with a simple initial solution and progressively improves it through two rounds of review.
        This approach systematically addresses potential oversights or inaccuracies in the first attempt,
        mimicking how humans refine their thinking when solving complex problems.
        """
        # Step 1: Generate a basic solution with minimal guidance
        initial_solution = await self.custom(
            instruction="Solve the problem directly without overcomplicating. Just give the answer."
        )

        # Step 2: First round of refinement — improve clarity and correctness
        refined_solution_1 = await self.review(
            pre_solution=initial_solution
        )

        # Step 3: Second round of refinement — ensure logical consistency and completeness
        refined_solution_2 = await self.review(
            pre_solution=refined_solution_1
        )

        return refined_solution_2
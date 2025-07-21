# Workflow ID: gsm8k_85_1
# Benchmark: gsm8k
# Data Indices: [242, 952]

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
        This mimics how humans refine their reasoning — first draft, then feedback, then polish.
        """
        # Step 1: Generate an initial solution (simple but clear)
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Focus on clarity over completeness."
        )

        # Step 2: First refinement — improve based on structured critique
        refined_solution_1 = await self.review(
            pre_solution=initial_solution
        )

        # Step 3: Second refinement — apply deeper scrutiny to catch subtle issues
        refined_solution_2 = await self.review(
            pre_solution=refined_solution_1
        )

        return refined_solution_2
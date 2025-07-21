# Workflow ID: gsm8k_74_1
# Benchmark: gsm8k
# Data Indices: [315, 16]

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
        This is an iterative refinement workflow using the 'Iterative Refinement' pattern.
        It starts with a basic solution and progressively improves it through two rounds of review.
        This mimics how humans refine their reasoning — first draft, then polish, then polish again.
        """
        # Step 1: Generate a simple initial solution using step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into clear steps. "
                        "Focus on getting a correct answer, even if the explanation is basic."
        )

        # Step 2: First round of refinement — improve clarity and logic
        refined_solution_1 = await self.review(
            pre_solution=initial_solution
        )

        # Step 3: Second round of refinement — address deeper logical issues or missing elements
        refined_solution_2 = await self.review(
            pre_solution=refined_solution_1
        )

        return refined_solution_2
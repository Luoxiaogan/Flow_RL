# Workflow ID: gsm8k_312_1
# Benchmark: gsm8k
# Data Indices: [601, 640]

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
        This is a diverse workflow using the 'Iterative Refinement' pattern.
        It generates an initial solution and then applies the `Review` operator twice
        to progressively improve it — mimicking how humans refine their thinking through
        multiple passes of critique and revision. This approach emphasizes iterative
        learning over single-shot reasoning.
        """
        # Step 1: Generate an initial rough solution with minimal structure
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, even if your answer seems incomplete or unclear."
        )

        # Step 2: First refinement pass — review and improve the initial attempt
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — further polish based on the first revision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
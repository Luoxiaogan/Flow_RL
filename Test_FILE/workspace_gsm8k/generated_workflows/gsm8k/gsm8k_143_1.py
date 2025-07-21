# Workflow ID: gsm8k_143_1
# Benchmark: gsm8k
# Data Indices: [225, 749]

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
        It starts with a simple initial solution and applies the `Review` operator twice to progressively improve it.
        This mimics how humans refine their thinking through multiple passes — first identifying surface issues, then deeper ones.
        """
        # Step 1: Generate a basic solution using a minimal instruction — just "solve the problem"
        initial_solution = await self.custom(
            instruction="Solve the problem. Be clear but concise."
        )

        # Step 2: First refinement — review the initial solution for clarity, logic gaps, or missing steps
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply another round of review to catch subtler flaws or inefficiencies
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
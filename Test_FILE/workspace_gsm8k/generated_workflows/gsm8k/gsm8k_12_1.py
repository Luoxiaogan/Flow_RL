# Workflow ID: gsm8k_12_1
# Benchmark: gsm8k
# Data Indices: [801, 422, 633]

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
        It starts with a simple solution, then applies the Review operator twice to progressively improve it.
        This mimics how humans refine their thinking — first draft, then edit, then polish — leading to higher accuracy.
        """
        # Step 1: Generate an initial solution using a basic custom call (no structured steps)
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: First refinement — review the initial solution for clarity, logic, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply another round of review to catch subtle errors or missing elements
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
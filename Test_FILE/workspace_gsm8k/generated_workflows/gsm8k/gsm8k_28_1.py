# Workflow ID: gsm8k_28_1
# Benchmark: gsm8k
# Data Indices: [275, 80]

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
        It generates an initial solution, then applies the Review operator twice to progressively improve it.
        This mimics how humans refine their thinking through repeated scrutiny — not by starting over, but by iteratively enhancing.
        """
        # Step 1: Generate a baseline solution with clear reasoning
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down the problem into logical parts."
        )

        # Step 2: First refinement — review the initial solution for clarity, logic gaps, or missing steps
        current_solution = await self.review(pre_solution=current_solution)

        # Step 3: Second refinement — apply another round of review to catch subtler issues or inconsistencies
        current_solution = await self.review(pre_solution=current_solution)

        return current_solution
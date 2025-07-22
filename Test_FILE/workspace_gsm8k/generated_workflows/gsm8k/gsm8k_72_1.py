# Workflow ID: gsm8k_72_1
# Benchmark: gsm8k
# Data Indices: [687, 330]

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
        It starts with an initial solution, then applies the `Review` operator twice to progressively improve it.
        This mimics how humans refine their reasoning through multiple passes — each time catching errors or gaps missed earlier.
        Unlike the existing workflow (which uses Reflect + Custom), this one focuses on direct iterative improvement via critique.
        """
        # Step 1: Generate an initial solution with clear reasoning
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down each part logically."
        )

        # Step 2: Apply Review at least twice for iterative refinement
        for iteration in range(2):
            current_solution = await self.review(pre_solution=current_solution)

        return current_solution
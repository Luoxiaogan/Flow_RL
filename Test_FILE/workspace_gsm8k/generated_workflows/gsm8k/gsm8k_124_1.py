# Workflow ID: gsm8k_124_1
# Benchmark: gsm8k
# Data Indices: [859, 336]

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
        It starts with a simple initial solution, then applies the `Review` operator twice
        to progressively improve it — each time refining assumptions, clarifying logic, and
        strengthening mathematical reasoning. This mimics how humans iteratively debug and
        enhance their solutions when they encounter subtle errors or ambiguities.
        """

        # Step 1: Generate an initial solution using a basic step-by-step instruction
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step. Show all calculations clearly."
        )

        # Step 2: Apply iterative refinement — first review
        current_solution = await self.review(pre_solution=current_solution)

        # Step 3: Apply second review for deeper refinement
        current_solution = await self.review(pre_solution=current_solution)

        return current_solution
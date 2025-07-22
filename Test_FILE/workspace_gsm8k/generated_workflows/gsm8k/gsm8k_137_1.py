# Workflow ID: gsm8k_137_1
# Benchmark: gsm8k
# Data Indices: [529, 686]

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
        It starts with a simple initial solution and applies the Review operator twice
        to progressively improve it—first by identifying flaws, then by enhancing clarity and correctness.
        This structure ensures iterative improvement without branching or parallelism,
        making it fundamentally different from the existing workflow which uses Reflect + Custom regeneration.
        """

        # Step 1: Generate an initial solution using a basic custom call
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear and concise."
        )

        # Step 2: First refinement — use Review to critique and improve the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply Review again to further polish the solution
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
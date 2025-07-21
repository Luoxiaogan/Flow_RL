# Workflow ID: gsm8k_91_1
# Benchmark: gsm8k
# Data Indices: [424, 176]

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
        This mimics how humans refine their reasoning through multiple passes — first catching surface errors,
        then addressing deeper logical gaps. The simplicity of this structure ensures clarity while enabling
        meaningful iterative improvement without overcomplicating the flow.
        """
        # Step 1: Generate a simple, initial solution using a basic custom instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each part clearly."
        )

        # Step 2: Apply iterative refinement — first review to fix obvious issues
        first_revision = await self.review(pre_solution=initial_solution)

        # Step 3: Apply second review to catch subtler flaws or inconsistencies
        second_revision = await self.review(pre_solution=first_revision)

        return second_revision
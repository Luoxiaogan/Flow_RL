# Workflow ID: gsm8k_258_1
# Benchmark: gsm8k
# Data Indices: [768, 228]

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
        It starts with a simple initial solution and applies the `Review` operator twice
        to progressively improve it — mimicking how humans refine their thinking through
        multiple passes of critical evaluation. This logic is fundamentally different from
        the existing 'Reflect and Regenerate' approach because it avoids reflection-based
        guidance and instead uses repeated, direct feedback loops on the same solution.
        """
        # Step 1: Generate a basic, straightforward solution
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step in a clear and concise manner."
        )

        # Step 2: Apply iterative refinement — review once to catch obvious errors
        current_solution = await self.review(pre_solution=current_solution)

        # Step 3: Review again for deeper logical consistency and completeness
        current_solution = await self.review(pre_solution=current_solution)

        return current_solution
# Workflow ID: gsm8k_129_1
# Benchmark: gsm8k
# Data Indices: [711, 231]

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
        It generates an initial solution and then applies the `Review` operator twice to progressively improve it.
        This mimics how humans refine their reasoning through multiple passes — each time catching errors or ambiguities missed earlier.
        """
        # Step 1: Generate an initial solution using general step-by-step reasoning
        current_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Explain each step clearly."
        )

        # Step 2: Apply iterative refinement — review once to catch obvious flaws
        current_solution = await self.review(pre_solution=current_solution)

        # Step 3: Review again for deeper logical consistency and clarity
        current_solution = await self.review(pre_solution=current_solution)

        return current_solution
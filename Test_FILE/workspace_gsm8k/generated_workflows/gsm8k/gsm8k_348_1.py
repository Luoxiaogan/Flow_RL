# Workflow ID: gsm8k_348_1
# Benchmark: gsm8k
# Data Indices: [56, 612, 349]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern.
        It starts with a simple initial solution, then applies the `Review` operator twice
        to progressively improve it — mimicking how humans refine their reasoning through
        multiple passes of critical evaluation. This logic differs from the existing
        'Reflect and Regenerate' approach by focusing on iterative critique rather than
        reflection-guided regeneration.
        """
        # Step 1: Generate a basic, straightforward solution
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations clearly."
        )

        # Step 2: Apply Review operator once to improve the solution
        improved_solution = await self.review(pre_solution=current_solution)

        # Step 3: Apply Review operator again for further refinement
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution
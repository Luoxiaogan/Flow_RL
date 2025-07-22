# Workflow ID: gsm8k_167_1
# Benchmark: gsm8k
# Data Indices: [485, 397, 940]

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
        This is a diverse and efficient workflow using Iterative Refinement with Review.
        It starts with an initial solution and applies progressive refinement through two Review steps.
        This differs from the existing workflow by focusing on iterative improvement via Review (not Reflect),
        avoiding meta-cognition and instead relying on direct critique and rewrite cycles.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        current_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Apply iterative refinement — review twice to progressively improve the solution
        for i in range(2):  # Two rounds of refinement
            current_solution = await self.review(pre_solution=current_solution)

        return current_solution
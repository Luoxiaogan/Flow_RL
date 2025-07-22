# Workflow ID: gsm8k_3_0
# Benchmark: gsm8k
# Data Indices: [506, 353, 139]

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
        Iterative Refinement Workflow: Generate an initial solution, then refine it twice using Review.
        This pattern ensures progressive improvement through structured critique and rewriting.
        """
        # Step 1: Generate a basic solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: First refinement via Review — improve clarity, logic, or completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review — address any remaining issues
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
# Workflow ID: gsm8k_183_0
# Benchmark: gsm8k
# Data Indices: [832, 471]

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
        Iterative Refinement Workflow: Start with a basic solution, then refine it twice using Review.
        This pattern ensures logical progression and improved accuracy through structured feedback loops.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining each reasoning phase clearly.")

        # Step 2: First refinement — improve based on internal critique
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further polish the already-improved solution
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
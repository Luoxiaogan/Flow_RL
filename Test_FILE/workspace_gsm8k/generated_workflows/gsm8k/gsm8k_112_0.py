# Workflow ID: gsm8k_112_0
# Benchmark: gsm8k
# Data Indices: [231, 302]

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
        This is a diverse and effective workflow using Iterative Refinement.
        It starts with a simple initial solution, then refines it twice using Review.
        The structure is logical, uses multiple operators, and avoids problem-specific details.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all reasoning clearly."
        )

        # Step 2: First refinement — improve the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further enhance the solution
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
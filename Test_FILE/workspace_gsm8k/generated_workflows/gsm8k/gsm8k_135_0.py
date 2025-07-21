# Workflow ID: gsm8k_135_0
# Benchmark: gsm8k
# Data Indices: [900, 336, 932]

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
        This is a diverse workflow using the Iterative Refinement pattern.
        It starts with a basic solution and improves it through two rounds of review.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations clearly."
        )

        # Step 2: First refinement via Review — improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review — catch any remaining errors or ambiguities
        second_refined = await self.review(pre_solution=first_refined)

        # Return the final improved solution
        return second_refined
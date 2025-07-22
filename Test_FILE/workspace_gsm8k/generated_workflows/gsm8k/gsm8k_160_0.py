# Workflow ID: gsm8k_160_0
# Benchmark: gsm8k
# Data Indices: [544, 924]

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
        Iterative Refinement Workflow using the 'Review' operator twice.
        This is a diverse and effective structure that improves reasoning through progressive critique.
        """
        # Step 1: Generate an initial solution with clear, step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into clear steps: identify knowns, apply formulas, compute final result."
        )

        # Step 2: First refinement via Review — improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review — catch any remaining issues or ambiguities
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
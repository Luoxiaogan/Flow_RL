# Workflow ID: gsm8k_90_0
# Benchmark: gsm8k
# Data Indices: [184, 891, 135]

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
        Iterative Refinement Workflow: Generate an initial solution, then improve it through two rounds of review.
        This pattern ensures gradual refinement without requiring parallel processing or complex branching.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each reasoning step clearly and logically."
        )

        # Step 2: First round of refinement via Review — improve clarity, structure, and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second round of refinement — further polish for accuracy and completeness
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
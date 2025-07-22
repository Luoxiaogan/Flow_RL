# Workflow ID: gsm8k_387_0
# Benchmark: gsm8k
# Data Indices: [375, 109, 566]

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
        This structure ensures logical progression and progressive quality enhancement without relying on ensembling or reflection-based regeneration.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning pattern
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "plan", "solve", "verify"],
            custom_instruction="Solve the problem step-by-step with clear reasoning."
        )

        # Step 2: First refinement — critique and rewrite the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further improve based on the first revision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
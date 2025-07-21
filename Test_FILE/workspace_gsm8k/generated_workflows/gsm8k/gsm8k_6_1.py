# Workflow ID: gsm8k_6_1
# Benchmark: gsm8k
# Data Indices: [32, 494]

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
        This is a diverse workflow using the 'Iterative Refinement' pattern.
        It starts with a basic solution and progressively improves it through two rounds of review.
        This mimics how humans refine their thinking — first draft, then critique, then polish.
        """
        # Step 1: Generate an initial solution using flexible custom in sequential mode for clarity
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, solving each part logically.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "compute", "verify"]
        )

        # Step 2: First refinement — use Review to improve clarity, structure, and logic
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply Review again to catch any remaining errors or ambiguities
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
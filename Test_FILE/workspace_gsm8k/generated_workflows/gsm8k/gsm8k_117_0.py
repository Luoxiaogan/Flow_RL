# Workflow ID: gsm8k_117_0
# Benchmark: gsm8k
# Data Indices: [145, 478, 579]

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
        This pattern ensures progressive enhancement by systematically identifying and correcting flaws.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"],
            custom_instruction="Break the problem into clear logical steps and solve step-by-step."
        )

        # Step 2: First refinement via Review - Improve clarity, logic, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review - Address any remaining issues or ambiguities
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
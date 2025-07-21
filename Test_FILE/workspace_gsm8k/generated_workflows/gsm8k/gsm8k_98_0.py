# Workflow ID: gsm8k_98_0
# Benchmark: gsm8k
# Data Indices: [319, 317, 145]

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
        This pattern ensures progressive enhancement by identifying and correcting flaws in each iteration.
        """
        # Step 1: Generate an initial solution using a structured, step-by-step approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem systematically into knowns, unknowns, and steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "apply_calculation", "verify_result"]
        )

        # Step 2: First refinement via Review — improve clarity, logic, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review — focus on accuracy, consistency, and potential oversights
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
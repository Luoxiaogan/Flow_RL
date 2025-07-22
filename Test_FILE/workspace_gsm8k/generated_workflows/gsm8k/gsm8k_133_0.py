# Workflow ID: gsm8k_133_0
# Benchmark: gsm8k
# Data Indices: [925, 53]

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
        This pattern ensures progressive improvement by addressing potential oversights in each iteration.
        """
        # Step 1: Initial solution via flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying all relevant quantities and operations needed to solve the problem.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_operations", "perform_calculation", "present_answer"]
        )

        # Step 2: First refinement — review the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further improve based on the first revision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
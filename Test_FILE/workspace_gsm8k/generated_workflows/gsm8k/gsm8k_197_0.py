# Workflow ID: gsm8k_197_0
# Benchmark: gsm8k
# Data Indices: [474, 752, 16]

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
        Iterative Refinement Workflow: Generate an initial solution and improve it through two rounds of review.
        This structure emphasizes progressive enhancement over a single attempt, increasing accuracy by addressing flaws incrementally.
        """
        # Step 1: Generate an initial solution using a flexible custom approach with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying key elements and applying logical steps in sequence.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_result"]
        )

        # Step 2: First refinement pass — critique and improve the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — further enhance based on the first improvement
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
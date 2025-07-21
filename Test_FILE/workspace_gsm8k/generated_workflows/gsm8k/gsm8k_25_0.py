# Workflow ID: gsm8k_25_0
# Benchmark: gsm8k
# Data Indices: [483, 685, 764]

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
        This pattern ensures progressive quality enhancement without requiring multiple independent paths.
        """
        # Step 1: Generate a basic solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break the problem into clear logical steps and solve systematically."
        )

        # Step 2: First refinement pass — critique and rewrite
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — further improve based on the first revision
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
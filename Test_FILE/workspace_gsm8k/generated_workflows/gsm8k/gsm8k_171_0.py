# Workflow ID: gsm8k_171_0
# Benchmark: gsm8k
# Data Indices: [982, 368]

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
        This pattern ensures progressive improvement by focusing on logical consistency and completeness.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break the problem into clear steps: identify inputs, compute each part, then combine."
        )

        # Step 2: First refinement — improve clarity, structure, and accuracy
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — address potential oversights or missing elements
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        return refined_solution_2
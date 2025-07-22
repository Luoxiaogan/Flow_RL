# Workflow ID: gsm8k_126_0
# Benchmark: gsm8k
# Data Indices: [745, 354]

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
        This structure ensures logical progression and iterative enhancement without relying on ensembling or reflection-based regeneration.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin with a clear, step-by-step breakdown of the problem.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "solve", "verify"]
        )

        # Step 2: First refinement via Review - improve clarity, logic flow, and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review - focus on potential errors, edge cases, or missing assumptions
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
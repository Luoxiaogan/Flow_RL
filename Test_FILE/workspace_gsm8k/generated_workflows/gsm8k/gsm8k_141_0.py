# Workflow ID: gsm8k_141_0
# Benchmark: gsm8k
# Data Indices: [737, 964]

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
        This is a diverse workflow using Iterative Refinement with FlexibleCustom for structured reasoning.
        First, we generate an initial solution using a sequential pattern. Then, we refine it twice via Review.
        """
        # Step 1: Generate initial solution using Sequential FlexibleCustom for structured breakdown
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem logically step-by-step.",
            reasoning_pattern="sequential",
            steps=["understand", "identify_knowns", "formulate_plan", "execute", "verify"]
        )

        # Step 2: First refinement - improve based on review
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement - further improve the already improved solution
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
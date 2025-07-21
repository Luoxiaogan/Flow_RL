# Workflow ID: gsm8k_139_0
# Benchmark: gsm8k
# Data Indices: [957, 696, 187]

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
        This pattern ensures progressive improvement by systematically addressing weaknesses in each iteration.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin with a clear breakdown of the problem into knowns and unknowns.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "formulate_plan", "execute_calculation"]
        )

        # Step 2: First refinement - review the initial solution for clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement - apply another round of review to catch any remaining issues
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
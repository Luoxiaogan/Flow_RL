# Workflow ID: gsm8k_34_0
# Benchmark: gsm8k
# Data Indices: [757, 534]

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
        This pattern ensures gradual improvement by progressively addressing weaknesses in the solution.
        """
        # Step 1: Generate a basic solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem logically and solve step-by-step."
        )

        # Step 2: First refinement — improve clarity, logic, or completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — address any remaining issues (e.g., edge cases, assumptions)
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
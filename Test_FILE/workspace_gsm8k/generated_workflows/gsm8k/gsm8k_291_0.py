# Workflow ID: gsm8k_291_0
# Benchmark: gsm8k
# Data Indices: [473, 801, 11]

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
        Iterative Refinement Workflow for General Mathematical Problem Solving
        This workflow generates an initial solution, then applies two rounds of review
        to progressively improve clarity, accuracy, and logical structure.
        """

        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break the problem into smaller parts and solve step-by-step."
        )

        # Step 2: First refinement via Review - improve clarity and logic flow
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review - address any lingering gaps or assumptions
        second_refined = await self.review(pre_solution=first_refined)

        # Final output: return the fully refined solution
        return second_refined
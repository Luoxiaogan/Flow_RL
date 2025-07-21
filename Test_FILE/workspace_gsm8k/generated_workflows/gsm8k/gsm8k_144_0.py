# Workflow ID: gsm8k_144_0
# Benchmark: gsm8k
# Data Indices: [550, 681]

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
        Iterative Refinement Workflow using the Review operator twice for progressive improvement.
        This is a diverse and logically structured approach that avoids a single-step solution.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller steps. First, identify what needs to be calculated. Then, perform each calculation systematically. Finally, verify your result."
        )

        # Step 2: First refinement using Review - improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement using Review - catch any remaining errors or ambiguities
        second_refined = await self.review(pre_solution=first_refined)

        # Optional: Use Reflect to generate a critique of the final refined solution (for potential future use in more advanced workflows)
        reflection = await self.reflect(pre_solution=second_refined)

        # Return the most improved version after two rounds of review
        return second_refined
# Benchmark: GSM8K
# Workflow ID: gsm8k_26
# Data Indices: [290, 291, 292]
# Generation Time: 2025-07-17 20:55:24
# Status: generated
# ==================================================

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

    async def run_workflow(self):
        """
        This is a diverse and adaptive workflow for solving mathematical problems.
        It uses a combination of reflection, review, and ensemble techniques to ensure robustness.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the solution to identify potential issues or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution
        refined_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution."
        )

        # Step 4: Optionally, perform a review to further refine the solution
        reviewed_solution = await self.review(pre_solution=refined_solution)

        # Step 5: Return the final solution
        return reviewed_solution
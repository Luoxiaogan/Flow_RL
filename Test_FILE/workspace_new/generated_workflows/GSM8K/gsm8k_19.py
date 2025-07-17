# Benchmark: GSM8K
# Workflow ID: gsm8k_19
# Data Indices: [220, 221, 222]
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
        This is a diverse workflow that combines reflection, iterative refinement, and ensemble-based solution selection.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential issues or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a revised solution
        revised_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution."
        )

        # Step 4: Perform a review to further refine the solution
        final_solution = await self.review(pre_solution=revised_solution)

        # Step 5: Use ScEnsemble to compare multiple solutions (in this case, just the final one)
        best_solution = await self.sc_ensemble(solutions=[final_solution])

        return best_solution
# Benchmark: GSM8K
# Workflow ID: gsm8k_0
# Data Indices: [30, 31, 32]
# Generation Time: 2025-07-17 22:42:07
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
        A diverse workflow using iterative refinement with reflection and review.
        """
        # Step 1: Generate an initial solution
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential issues
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a refined solution
        refined_solution = await self.custom(instruction=f"Based on the following reflection: {reflection}. Now, provide a new, improved solution.")

        # Step 4: Review the refined solution to further improve it
        reviewed_solution = await self.review(pre_solution=refined_solution)

        # Step 5: Final review for any remaining improvements
        final_solution = await self.review(pre_solution=reviewed_solution)

        return final_solution
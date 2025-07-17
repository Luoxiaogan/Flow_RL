# Benchmark: GSM8K
# Workflow ID: gsm8k_11
# Data Indices: [140, 141, 142]
# Generation Time: 2025-07-17 20:55:21
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
        This is a diverse workflow that combines reflection and iterative refinement.
        It first generates an initial solution, reflects on it, and then uses that reflection to guide a refined solution.
        """

        # Step 1: Generate an initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to generate a more refined solution
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}', provide a revised and improved solution."
        )

        # Step 4: Optionally review the refined solution for final quality
        final_solution = await self.review(
            pre_solution=refined_solution
        )

        return final_solution
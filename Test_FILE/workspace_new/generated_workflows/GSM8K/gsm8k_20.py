# Benchmark: GSM8K
# Workflow ID: gsm8k_20
# Data Indices: [230, 231, 232]
# Generation Time: 2025-07-17 20:55:27
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
        This is a workflow graph.
        """
        # Step 1: Generate an initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the solution to identify potential flaws or missing steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, more refined solution
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: {reflection}. "
                        "Re-solve the problem with this insight in mind."
        )

        # Step 4: Optionally review the refined solution for clarity and correctness
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution
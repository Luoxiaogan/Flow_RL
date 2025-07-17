# Benchmark: GSM8K
# Workflow ID: gsm8k_24
# Data Indices: [270, 271, 272]
# Generation Time: 2025-07-17 20:55:20
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
        This workflow uses a Reflect-and-Regenerate pattern to iteratively improve the solution.
        It first generates an initial solution, reflects on it, and then regenerates a more accurate one.
        """

        # Step 1: Generate an initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Regenerate a refined solution based on the reflection
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. "
                        "Revise the solution with this insight in mind. Provide a detailed, accurate answer."
        )

        # Step 4: Optionally review the refined solution for further improvements
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution
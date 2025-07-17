# Benchmark: GSM8K
# Workflow ID: gsm8k_13
# Data Indices: [160, 161, 162]
# Generation Time: 2025-07-17 21:02:41
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
        This workflow uses a reflective and iterative approach to solve mathematical problems.
        It first generates an initial solution, reflects on it, and then refines it based on that reflection.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution to identify potential issues or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a more refined solution
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. "
                        "Please provide a more accurate and detailed solution based on this reflection."
        )

        # Step 4: Optionally review the refined solution for further improvement
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution
# Benchmark: GSM8K
# Workflow ID: gsm8k_4
# Data Indices: [70, 71, 72]
# Generation Time: 2025-07-17 22:42:08
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
        This workflow combines a Parallel Ensemble with a Reflect and Regenerate pattern.
        It generates multiple solutions, selects the best one, reflects on it, and then regenerates
        a refined solution based on that reflection.
        """

        # Step 1: Generate multiple initial solutions using a loop
        solution_list = []
        for _ in range(3):  # Generate 3 different solutions
            solution = await self.custom(
                instruction="Solve the problem step-by-step, explaining your reasoning clearly."
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution from the list
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect on the best solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, more refined solution
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}, provide a new, improved solution to the problem."
        )

        # Step 5: Optionally review the final solution for clarity and correctness
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution
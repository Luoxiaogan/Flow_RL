# Benchmark: GSM8K
# Workflow ID: gsm8k_39
# Data Indices: [420, 421, 422]
# Generation Time: 2025-07-17 21:02:46
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
        This is a diverse workflow for solving mathematical problems.
        It uses reflection, parallel solutions, and iterative refinement.
        """

        # Step 1: Generate multiple initial solutions using parallel ensemble
        solution1 = await self.custom(instruction="Solve the problem step-by-step.")
        solution2 = await self.custom(instruction="Break down the problem into parts and solve each part.")
        solution3 = await self.custom(instruction="Use a diagram or visual model to represent the problem.")

        # Step 2: Use ScEnsemble to select the best among the three solutions
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Reflect on the best solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: {reflection}. "
                        "Re-solve the problem with this insight in mind."
        )

        # Step 5: Review the improved solution for clarity and correctness
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution
# Benchmark: GSM8K
# Workflow ID: gsm8k_27
# Data Indices: [300, 301, 302]
# Generation Time: 2025-07-17 21:02:42
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
        This is a diverse workflow that uses multiple reasoning structures:
        - Parallel Ensemble for robustness
        - Reflect and Regenerate for meta-cognitive improvement
        - Iterative Review for refinement
        """

        # Step 1: Generate multiple initial solutions using parallel ensemble
        solution1 = await self.custom(instruction="Solve the problem step-by-step with detailed reasoning.")
        solution2 = await self.custom(instruction="Break down the problem into smaller parts and solve each one.")
        solution3 = await self.custom(instruction="Use logical deduction to arrive at the answer.")

        # Step 2: Use ScEnsemble to select the best solution from the three
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Reflect on the best solution to identify potential flaws or alternative approaches
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Now, provide a refined and accurate solution."
        )

        # Step 5: Optionally review the improved solution for further refinement
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution
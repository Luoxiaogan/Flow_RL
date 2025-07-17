# Benchmark: GSM8K
# Workflow ID: gsm8k_22
# Data Indices: [250, 251, 252]
# Generation Time: 2025-07-17 20:55:26
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
        This is a diverse workflow for solving math problems.
        It uses reflection, iteration, and ensemble methods.
        """

        # Step 1: Generate an initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a refined solution
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Now, provide a more accurate solution."
        )

        # Step 4: Generate multiple alternative solutions in parallel
        solution1 = await self.custom(
            instruction="Solve the problem using a different method or perspective."
        )
        solution2 = await self.custom(
            instruction="Solve the problem by focusing on the relationships between quantities."
        )
        solution3 = await self.custom(
            instruction="Solve the problem using algebraic equations."
        )

        # Step 5: Use ScEnsemble to select the best solution
        best_solution = await self.sc_ensemble(solutions=[initial_solution, refined_solution, solution1, solution2, solution3])

        # Step 6: Optionally review the best solution for final polish
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
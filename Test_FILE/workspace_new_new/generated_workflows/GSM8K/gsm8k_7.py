# Benchmark: GSM8K
# Workflow ID: gsm8k_7
# Data Indices: [100, 101, 102]
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
        self.reflect = operator.Reflect(self.config, self.problem)  # New operator

    async def run_workflow(self):
        """
        A diverse, multi-step workflow for solving mathematical problems.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the solution to identify potential flaws or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a refined solution
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}, re-solve the problem with more attention to detail."
        )

        # Step 4: Generate multiple alternative solutions using parallel ensembles
        ensemble_solutions = [
            await self.custom(instruction="Solve the problem from a different perspective.")
            for _ in range(3)
        ]

        # Step 5: Use ScEnsemble to select the best solution from the alternatives
        best_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        # Step 6: Review the best solution to ensure clarity and correctness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
# Benchmark: GSM8K
# Workflow ID: gsm8k_20
# Data Indices: [230, 231, 232]
# Generation Time: 2025-07-17 21:02:49
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
        This is a meta-cognitive, ensemble-based workflow for solving math problems.
        """

        # Step 1: Generate an initial solution
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a second solution based on the reflection
        revised_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. Now, provide a new, improved solution."
        )

        # Step 4: Generate a third solution independently (ensemble approach)
        alternative_solution = await self.custom(
            instruction="Solve the problem using a different approach or perspective."
        )

        # Step 5: Use ScEnsemble to select the best solution from the three
        solutions = [initial_solution, revised_solution, alternative_solution]
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Optionally refine the best solution further using Review
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
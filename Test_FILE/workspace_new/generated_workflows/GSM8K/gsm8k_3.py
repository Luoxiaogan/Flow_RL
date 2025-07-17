# Benchmark: GSM8K
# Workflow ID: gsm8k_3
# Data Indices: [60, 61, 62]
# Generation Time: 2025-07-17 20:55:29
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
        This is a workflow graph that uses reflection, iteration, and ensemble methods.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the solution to identify potential issues or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a revised solution
        revised_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution."
        )

        # Step 4: Generate multiple alternative solutions using parallel ensembles
        solution_list = [
            await self.custom(instruction="Solve the problem from a different perspective."),
            await self.custom(instruction="Use a more formal mathematical approach to solve this problem."),
            await self.custom(instruction="Break down the problem into smaller subproblems and solve each one.")
        ]

        # Step 5: Use ScEnsemble to select the best solution from the alternatives
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 6: Review the best solution for clarity, accuracy, and completeness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
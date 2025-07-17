# Benchmark: GSM8K
# Workflow ID: gsm8k_27
# Data Indices: [300, 301, 302]
# Generation Time: 2025-07-17 20:55:24
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
        This is a diverse workflow that combines reflection, ensemble evaluation, and iterative refinement.
        It first generates an initial solution, reflects on it, and then uses that reflection to guide a more refined solution.
        Additionally, it creates multiple solutions and selects the best one.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential issues or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a revised solution
        revised_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution."
        )

        # Step 4: Generate multiple independent solutions using parallel ensembles
        solution_list = [
            await self.custom(instruction="Solve the problem by breaking it into smaller steps and checking each part carefully."),
            await self.custom(instruction="Use logical deduction to solve the problem and verify each step.")
        ]

        # Step 5: Use ScEnsemble to select the best solution from the list
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 6: Optionally refine the best solution further using Review
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
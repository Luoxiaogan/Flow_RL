# Benchmark: GSM8K
# Workflow ID: gsm8k_2
# Data Indices: [50, 51, 52]
# Generation Time: 2025-07-17 20:55:23
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
        This is a diverse and adaptive workflow for solving mathematical problems.
        It combines reflection, iterative refinement, and ensemble-based solution selection.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the solution to identify potential flaws or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, more refined solution
        refined_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution."
        )

        # Step 4: Generate multiple alternative solutions using parallel ensembles
        solution1 = await self.custom(instruction="Approach the problem from a different angle.")
        solution2 = await self.custom(instruction="Use a visual or diagrammatic method to solve it.")
        solution3 = await self.custom(instruction="Break the problem into smaller sub-problems.")

        # Step 5: Use ScEnsemble to select the best among the generated solutions
        best_solution = await self.sc_ensemble(solutions=[initial_solution, refined_solution, solution1, solution2, solution3])

        # Step 6: Optionally review the best solution to further refine it
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
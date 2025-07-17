# Benchmark: GSM8K
# Workflow ID: gsm8k_17
# Data Indices: [200, 201, 202]
# Generation Time: 2025-07-17 21:02:43
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
        It first generates an initial solution, reflects on it, then uses the reflection to guide a new solution.
        Finally, it evaluates multiple solutions to select the best one.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution to identify potential issues or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a revised solution
        revised_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. Now, provide a more accurate or improved solution."
        )

        # Step 4: Generate additional solutions using parallel ensembles for robustness
        solution1 = await self.custom(
            instruction="Solve the problem using a different approach, focusing on clarity and structure."
        )
        solution2 = await self.custom(
            instruction="Break down the problem into smaller parts and solve each part independently."
        )
        solution3 = await self.custom(
            instruction="Use a visual or diagrammatic approach to represent the problem and its solution."
        )

        # Step 5: Use ScEnsemble to evaluate all generated solutions and select the best one
        solutions = [initial_solution, revised_solution, solution1, solution2, solution3]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution
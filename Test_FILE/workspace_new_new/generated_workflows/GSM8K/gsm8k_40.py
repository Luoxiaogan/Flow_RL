# Benchmark: GSM8K
# Workflow ID: gsm8k_40
# Data Indices: [430, 431, 432]
# Generation Time: 2025-07-17 21:02:44
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
        This is a diverse and structured workflow for solving mathematical problems.
        It combines iterative refinement, reflection, and ensemble-based selection.
        """

        # Step 1: Generate an initial solution using custom reasoning
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the solution to identify potential flaws or missing steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a revised solution
        revised_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}, re-solve the problem with more attention to detail."
        )

        # Step 4: Review the revised solution to improve clarity and correctness
        final_solution = await self.review(pre_solution=revised_solution)

        # Step 5: Generate multiple alternative solutions using parallel ensembles
        solution1 = await self.custom(instruction="Solve the problem from a different angle, such as by breaking it into parts.")
        solution2 = await self.custom(instruction="Use algebraic reasoning to solve the problem.")
        solution3 = await self.custom(instruction="Apply a visual or diagrammatic approach to the problem.")

        # Step 6: Use ScEnsemble to select the best solution from the alternatives
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 7: Final review of the best solution to ensure accuracy
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
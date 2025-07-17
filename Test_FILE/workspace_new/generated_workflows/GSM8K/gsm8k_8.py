# Benchmark: GSM8K
# Workflow ID: gsm8k_8
# Data Indices: [110, 111, 112]
# Generation Time: 2025-07-17 20:55:22
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
        This is a diverse workflow that combines reflection, review, and ensemble methods.
        It first generates an initial solution, reflects on it, then refines it with a custom prompt based on the reflection.
        Finally, it uses an ensemble to select the best answer from multiple generated solutions.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential issues or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution via Custom
        refined_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution."
        )

        # Step 4: Generate multiple alternative solutions using parallel Custom calls
        solution1 = await self.custom(instruction="Approach the problem from a different angle.")
        solution2 = await self.custom(instruction="Use a more mathematical or formula-based approach.")
        solution3 = await self.custom(instruction="Break the problem down into smaller, independent sub-problems.")

        # Step 5: Use ScEnsemble to select the best solution from the alternatives
        final_solution = await self.sc_ensemble(solutions=[initial_solution, refined_solution, solution1, solution2, solution3])

        return final_solution
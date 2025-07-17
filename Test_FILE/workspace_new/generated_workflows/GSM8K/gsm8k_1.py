# Benchmark: GSM8K
# Workflow ID: gsm8k_1
# Data Indices: [40, 41, 42]
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
        This is a diverse and adaptive workflow for solving mathematical problems.
        It uses a combination of reflection, refinement, and ensemble-based selection.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a revised solution
        revised_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Now, provide a more accurate or refined solution."
        )

        # Step 4: Optionally refine further using Review
        final_solution = await self.review(pre_solution=revised_solution)

        # Step 5: Return the final solution
        return final_solution
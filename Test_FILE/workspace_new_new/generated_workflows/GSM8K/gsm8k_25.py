# Benchmark: GSM8K
# Workflow ID: gsm8k_25
# Data Indices: [280, 281, 282]
# Generation Time: 2025-07-17 21:02:40
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
        This workflow uses a reflective and iterative approach to solve mathematical problems.
        It first generates an initial solution, reflects on it, and then refines it based on the reflection.
        """
        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a more refined solution
        refined_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution."
        )

        # Step 4: Optionally review the refined solution for clarity and accuracy
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution
# Benchmark: GSM8K
# Workflow ID: gsm8k_7
# Data Indices: [100, 101, 102]
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
        This is a diverse workflow that uses reflection and iterative refinement to solve mathematical problems.
        It first generates an initial solution, then reflects on it, and finally refines the solution based on the reflection.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a refined solution
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. Based on this, provide a more accurate and detailed solution."
        )

        # Step 4: Optionally review the refined solution for further improvements
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution
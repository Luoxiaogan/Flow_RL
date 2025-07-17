# Benchmark: GSM8K
# Workflow ID: gsm8k_12
# Data Indices: [150, 151, 152]
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
        It uses a combination of reflection, iterative refinement, and ensemble-based solution selection.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a more refined solution
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. "
                        "Now, provide a more accurate and detailed solution."
        )

        # Step 4: Optionally refine further using Review if needed
        final_solution = await self.review(pre_solution=refined_solution)

        # Step 5: If multiple solutions are available (e.g., from parallel processing), use ScEnsemble
        # For this example, we'll simulate a parallel ensemble by generating another solution
        alternative_solution = await self.custom(
            instruction="Solve the problem using a different approach, focusing on clarity and structure."
        )

        # Combine all solutions into a list and select the best one using ScEnsemble
        solutions = [final_solution, alternative_solution]
        best_solution = await self.sc_ensemble(solutions=solutions)

        return best_solution
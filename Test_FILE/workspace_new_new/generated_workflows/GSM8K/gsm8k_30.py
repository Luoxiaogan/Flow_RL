# Benchmark: GSM8K
# Workflow ID: gsm8k_30
# Data Indices: [330, 331, 332]
# Generation Time: 2025-07-17 21:02:41
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
        It uses a combination of reflection, iterative refinement, and ensemble-based selection.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a refined solution
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}, provide a more accurate and detailed solution."
        )

        # Step 4: Review the refined solution to improve it further
        final_solution = await self.review(pre_solution=refined_solution)

        # Step 5: Optionally, generate multiple solutions in parallel and select the best one
        parallel_solutions = [
            await self.custom(instruction="Solve the problem from a different angle."),
            await self.custom(instruction="Approach the problem using algebraic methods only.")
        ]
        best_solution = await self.sc_ensemble(solutions=parallel_solutions)

        # Step 6: Final review of the best solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
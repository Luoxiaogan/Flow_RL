# Benchmark: GSM8K
# Workflow ID: gsm8k_25
# Data Indices: [280, 281, 282]
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
        It uses a combination of reflection, iterative refinement, and ensemble-based solution selection.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a more refined solution
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. "
                        "Please provide a revised, improved solution based on this analysis."
        )

        # Step 4: Optionally, review the refined solution to further polish it
        final_solution = await self.review(pre_solution=refined_solution)

        # Step 5: If desired, generate multiple solutions in parallel and select the best one
        # (This is optional and can be toggled based on complexity)
        if self.config.get("use_ensemble", False):
            solution_list = [
                await self.custom(instruction="Solve the problem from scratch with a fresh approach."),
                await self.custom(instruction="Use a different method to solve the problem, such as algebraic manipulation.")
            ]
            final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution
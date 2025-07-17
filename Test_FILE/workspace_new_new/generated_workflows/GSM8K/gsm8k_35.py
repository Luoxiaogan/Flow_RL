# Benchmark: GSM8K
# Workflow ID: gsm8k_35
# Data Indices: [380, 381, 382]
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
        This is a diverse and adaptive workflow for solving mathematical problems.
        It uses a combination of reflection, refinement, and ensemble techniques.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential issues or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a more refined solution
        refined_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution."
        )

        # Step 4: Review the refined solution to enhance clarity and correctness
        final_solution = await self.review(pre_solution=refined_solution)

        # Step 5: Optionally generate multiple solutions and use ScEnsemble to select the best one
        # (This is a flexible addition that can be toggled based on problem complexity)
        if self.config.get("use_ensemble", False):
            solution_list = [
                await self.custom(instruction="Solve the problem in a different way, using a fresh approach."),
                await self.custom(instruction="Use a visual or diagram-based method to solve the problem.")
            ]
            final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution
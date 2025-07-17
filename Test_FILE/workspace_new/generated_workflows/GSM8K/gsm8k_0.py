# Benchmark: GSM8K
# Workflow ID: gsm8k_0
# Data Indices: [30, 31, 32]
# Generation Time: 2025-07-17 20:55:21
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
        This is a workflow graph that uses a Reflect and Regenerate pattern with a fallback to ScEnsemble.
        It first generates an initial solution, reflects on it, and then regenerates a better version.
        If the reflection leads to confusion, it falls back to ensemble-based selection.
        """

        # Step 1: Generate an initial solution
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a new solution
        guided_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. Based on this, provide a new, improved solution."
        )

        # Step 4: Optionally review the guided solution for refinement
        refined_solution = await self.review(pre_solution=guided_solution)

        # Step 5: If the solution seems ambiguous or uncertain, use ScEnsemble to select the best from multiple attempts
        solution_list = [initial_solution, guided_solution, refined_solution]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution
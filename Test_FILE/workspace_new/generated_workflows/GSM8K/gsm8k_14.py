# Benchmark: GSM8K
# Workflow ID: gsm8k_14
# Data Indices: [170, 171, 172]
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
        self.reflect = operator.Reflect(self.config, self.problem)  # New operator

    async def run_workflow(self):
        """
        This is a workflow graph that uses a hybrid approach of reflection and iterative refinement.
        It first generates an initial solution, then reflects on it to identify potential issues,
        and finally refines the solution based on that reflection.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the solution to identify potential flaws or areas for improvement
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to guide a more refined solution
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}, re-solve the problem with greater precision and clarity."
        )

        # Step 4: Optionally review the refined solution for further improvements
        final_solution = await self.review(
            pre_solution=refined_solution
        )

        return final_solution
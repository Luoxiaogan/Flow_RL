# Benchmark: GSM8K
# Workflow ID: gsm8k_1
# Data Indices: [40, 41, 42]
# Generation Time: 2025-07-17 21:02:42
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
        This is a workflow graph that uses a reflective and iterative approach to solve mathematical problems.
        It starts with an initial solution, reflects on it, and then refines it through multiple iterations.
        """

        # Step 1: Generate an initial solution using a custom instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or areas for improvement
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a more refined solution
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: {reflection}. "
                        "Now, provide a more accurate and detailed solution."
        )

        # Step 4: Review the refined solution to ensure clarity and correctness
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution
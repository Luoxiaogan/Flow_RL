# Benchmark: GSM8K
# Workflow ID: gsm8k_4
# Data Indices: [70, 71, 72]
# Generation Time: 2025-07-17 21:02:39
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
        It starts with an initial solution, reflects on it, and then refines the solution based on the reflection.
        """
        # Step 1: Generate an initial solution using a custom instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or areas for improvement
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a revised solution that addresses the identified issues
        revised_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Please provide a revised and improved solution."
        )

        # Step 4: Optionally review the revised solution for further refinement
        final_solution = await self.review(pre_solution=revised_solution)

        return final_solution
# Benchmark: GSM8K
# Workflow ID: gsm8k_2
# Data Indices: [50, 51, 52]
# Generation Time: 2025-07-17 22:42:05
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
        This workflow uses iterative refinement with review steps to improve a solution.
        It starts with an initial solution, then applies review twice to refine it.
        """
        # Step 1: Generate an initial solution
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Review the initial solution to identify improvements
        first_review = await self.review(pre_solution=initial_solution)

        # Step 3: Review the revised solution again for further refinement
        second_review = await self.review(pre_solution=first_review)

        return second_review
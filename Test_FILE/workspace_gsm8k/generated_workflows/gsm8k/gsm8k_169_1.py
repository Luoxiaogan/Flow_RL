# Workflow ID: gsm8k_169_1
# Benchmark: gsm8k
# Data Indices: [189, 622]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This workflow uses the Iterative Refinement pattern: 
        Generate an initial solution, then apply Review at least twice to progressively improve it.
        This mimics how humans refine their reasoning — first draft, then critique, then polish.
        """
        # Step 1: Generate a simple, initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Focus on clarity and completeness in your explanation."
        )

        # Step 2: First refinement — review the initial solution for errors or missing logic
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further improve based on the first revision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
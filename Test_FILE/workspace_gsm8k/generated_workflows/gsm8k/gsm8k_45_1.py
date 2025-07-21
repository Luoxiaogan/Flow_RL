# Workflow ID: gsm8k_45_1
# Benchmark: gsm8k
# Data Indices: [518, 539]

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
        Iterative Refinement Workflow: Starts with a basic solution and improves it through two rounds of review.
        This approach emphasizes progressive learning from critique rather than parallel exploration or branching.
        """
        # Step 1: Generate an initial solution using a simple, direct instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Focus on clarity and correctness."
        )

        # Step 2: Apply iterative refinement via Review twice to improve quality
        first_refinement = await self.review(pre_solution=initial_solution)
        second_refinement = await self.review(pre_solution=first_refinement)

        # Step 3: Final check to ensure no logical errors remain
        final_answer = await self.review(pre_solution=second_refinement)

        return final_answer
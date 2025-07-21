# Workflow ID: gsm8k_168_0
# Benchmark: gsm8k
# Data Indices: [413, 505, 445]

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
        This is a diverse and effective workflow using Iterative Refinement.
        It starts with an initial solution, then refines it twice using Review.
        This mimics how humans improve reasoning through multiple passes.
        """
        # Step 1: Generate an initial solution using a general instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into clear logical parts and explain each step."
        )

        # Step 2: First refinement pass — review to catch errors or gaps
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — further improve based on the first revision
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
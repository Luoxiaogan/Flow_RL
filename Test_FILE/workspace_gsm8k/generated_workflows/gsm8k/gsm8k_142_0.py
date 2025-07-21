# Workflow ID: gsm8k_142_0
# Benchmark: gsm8k
# Data Indices: [667, 301, 451]

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
        Iterative Refinement Workflow: Generate an initial solution and improve it through two rounds of review.
        This pattern ensures gradual quality improvement without needing multiple independent paths or complex branching.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into clear logical steps and explain each one."
        )

        # Step 2: First refinement pass — review to catch errors or omissions
        first_refinement = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — further polish based on the first review
        second_refinement = await self.review(pre_solution=first_refinement)

        return second_refinement
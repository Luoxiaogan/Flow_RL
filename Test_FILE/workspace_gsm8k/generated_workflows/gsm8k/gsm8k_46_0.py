# Workflow ID: gsm8k_46_0
# Benchmark: gsm8k
# Data Indices: [68, 932]

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
        This is a diverse workflow using Iterative Refinement with two Review steps.
        It starts with a simple initial solution, then refines it twice to improve clarity and correctness.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what is given. Then, determine what needs to be calculated. Finally, show your work clearly."
        )

        # Step 2: First refinement using Review to improve structure and logic
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement to catch any subtle errors or missing explanations
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
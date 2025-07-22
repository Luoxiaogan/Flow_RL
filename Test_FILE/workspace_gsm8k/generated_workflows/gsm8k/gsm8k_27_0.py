# Workflow ID: gsm8k_27_0
# Benchmark: gsm8k
# Data Indices: [681, 553, 88]

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
        Iterative Refinement Workflow: Generate an initial solution, then refine it twice using Review.
        This pattern ensures progressive improvement by identifying and correcting flaws step-by-step.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, breaking it into clear logical parts. Explain each step thoroughly."
        )

        # Step 2: First refinement - improve clarity, structure, and correctness
        first_refined = await self.review(
            pre_solution=initial_solution
        )

        # Step 3: Second refinement - focus on accuracy, completeness, and potential oversights
        second_refined = await self.review(
            pre_solution=first_refined
        )

        return second_refined
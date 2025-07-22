# Workflow ID: gsm8k_361_0
# Benchmark: gsm8k
# Data Indices: [470, 953, 573]

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
        This pattern ensures gradual improvement through structured feedback loops.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step. Break it down into clear logical steps and explain each one.")

        # Step 2: First refinement — review the initial solution for clarity, completeness, and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further improve based on the first review
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
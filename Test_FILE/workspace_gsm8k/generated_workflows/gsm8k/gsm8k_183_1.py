# Workflow ID: gsm8k_183_1
# Benchmark: gsm8k
# Data Indices: [832, 471]

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
        Iterative Refinement with Meta-Cognitive Reflection: 
        Start with a basic solution, then use Reflect to critique it before each Review step.
        This adds a layer of self-awareness to the refinement process, improving logical consistency and depth.
        """
        # Step 1: Generate an initial solution using general reasoning
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: First refinement cycle — reflect first, then review
        reflection_1 = await self.reflect(pre_solution=initial_solution)
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement cycle — reflect again on the improved version
        reflection_2 = await self.reflect(pre_solution=first_refined)
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
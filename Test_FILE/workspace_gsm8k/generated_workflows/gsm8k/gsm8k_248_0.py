# Workflow ID: gsm8k_248_0
# Benchmark: gsm8k
# Data Indices: [496, 457, 297]

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
        Iterative Refinement Workflow: Generate an initial solution and refine it twice using the Review operator.
        This pattern ensures progressive improvement by systematically addressing potential flaws or omissions.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each calculation clearly. Be precise and avoid assumptions."
        )

        # Step 2: First refinement pass — improve clarity, structure, and accuracy
        first_refined = await self.review(
            pre_solution=initial_solution
        )

        # Step 3: Second refinement pass — ensure completeness and correctness
        final_solution = await self.review(
            pre_solution=first_refined
        )

        return final_solution
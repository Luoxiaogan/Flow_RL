# Workflow ID: gsm8k_270_0
# Benchmark: gsm8k
# Data Indices: [717, 658, 999]

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
        This mimics human metacognition—solve, reflect, improve, repeat.
        """
        # Step 1: Generate a basic solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into logical parts and explain each step clearly."
        )

        # Step 2: First refinement via Review – improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement via Review – ensure no critical errors remain
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
# Workflow ID: gsm8k_19_1
# Benchmark: gsm8k
# Data Indices: [644, 246, 385]

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
        This workflow uses a Parallel Ensemble strategy to generate multiple solutions independently,
        then selects the best one using ScEnsemble. It's efficient, robust, and avoids over-reliance on a single reasoning path.
        """
        # Step 1: Generate three independent solutions using different prompts
        solution1 = await self.custom(
            instruction="Solve the problem by identifying known quantities first, then applying relevant formulas."
        )
        solution2 = await self.custom(
            instruction="Break the problem into smaller logical steps and solve each step sequentially."
        )
        solution3 = await self.custom(
            instruction="Think like a math tutor: explain your reasoning clearly as if teaching someone new to the topic."
        )

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return best_solution
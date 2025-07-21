# Workflow ID: gsm8k_79_1
# Benchmark: gsm8k
# Data Indices: [797, 551]

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
        This workflow uses a parallel ensemble strategy: generate 3 independent solutions using Custom,
        then select the best one via ScEnsemble. It's efficient, robust, and avoids over-reliance on a single reasoning path.
        """
        # Step 1: Generate multiple candidate solutions in parallel (independent reasoning paths)
        solution1 = await self.custom(instruction="Solve the problem step-by-step with clear explanations.")
        solution2 = await self.custom(instruction="Break down the problem into smaller parts and solve each systematically.")
        solution3 = await self.custom(instruction="Think through the problem as if teaching someone else—be explicit about every assumption and calculation.")

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        final_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return final_solution
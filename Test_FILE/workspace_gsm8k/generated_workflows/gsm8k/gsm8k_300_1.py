# Workflow ID: gsm8k_300_1
# Benchmark: gsm8k
# Data Indices: [950, 312]

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
        This is a diverse and efficient workflow using a parallel ensemble strategy.
        It generates multiple initial solutions independently, then selects the best one.
        This avoids single-point failures and leverages diversity in reasoning approaches.
        """
        # Step 1: Generate three independent solutions using different prompts to encourage varied reasoning paths
        solution1 = await self.custom(instruction="Solve the problem step-by-step with clear explanations.")
        solution2 = await self.custom(instruction="Break down the problem into smaller parts first, then solve each part systematically.")
        solution3 = await self.custom(instruction="First identify what is given and what needs to be found, then compute.")

        # Step 2: Use ScEnsemble to evaluate and select the most accurate solution from the three
        final_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return final_solution
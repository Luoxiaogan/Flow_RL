# Workflow ID: gsm8k_92_1
# Benchmark: gsm8k
# Data Indices: [995, 970, 540]

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
        This workflow uses the Parallel Ensemble pattern for robustness and efficiency.
        It generates 3 independent solutions using flexible custom reasoning, then selects the best one.
        This approach is simple yet effective — no single point of failure, minimal steps, and high reliability.
        """
        # Step 1: Generate multiple independent solutions using parallel reasoning
        solution_list = []
        for _ in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve this problem using a structured approach.",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        return best_solution
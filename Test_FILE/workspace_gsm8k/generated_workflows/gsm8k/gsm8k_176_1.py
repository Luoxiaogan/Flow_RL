# Workflow ID: gsm8k_176_1
# Benchmark: gsm8k
# Data Indices: [699, 762]

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
        This is a diverse workflow using the 'Parallel Ensemble' pattern.
        It generates multiple independent solutions using flexible custom with parallel reasoning,
        then selects the best one using ScEnsemble. This approach improves robustness by exploring
        different reasoning paths simultaneously.
        """
        # Step 1: Generate 3 independent solutions using parallel reasoning
        solution_list = []
        for _ in range(3):
            solution = await self.flexible_custom(
                reasoning_pattern="parallel",
                steps=["interpret", "model", "compute", "validate"],
                custom_instruction="Solve this problem from three different angles to ensure comprehensive reasoning."
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the pool
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution
# Workflow ID: gsm8k_113_1
# Benchmark: gsm8k
# Data Indices: [879, 584, 29]

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
        Parallel Ensemble + Iterative Refinement: Generate multiple initial solutions in parallel,
        then refine the best one iteratively to improve accuracy without overcomplicating the flow.
        This balances robustness and efficiency — a simple yet effective hybrid strategy.
        """
        # Step 1: Generate 3 independent solutions using parallel reasoning
        solution_pool = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step with clear reasoning.")
            solution_pool.append(sol)

        # Step 2: Select the best solution via ensemble
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Perform one round of refinement to polish the top candidate
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
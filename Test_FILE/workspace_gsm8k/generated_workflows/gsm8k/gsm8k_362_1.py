# Workflow ID: gsm8k_362_1
# Benchmark: gsm8k
# Data Indices: [816, 324, 643]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble + Reflect and Regenerate' pattern.
        It generates multiple initial solutions in parallel, selects the best one, then critically reflects on it
        before regenerating a superior final answer — ensuring both robustness and deep reasoning.
        """
        # Step 1: Generate multiple independent solutions using parallel approach
        solution_pool = []
        for _ in range(3):  # Create 3 different initial approaches
            solution = await self.custom(
                instruction="Solve the problem step-by-step using a unique strategy. Avoid repeating methods from other attempts."
            )
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to pick the strongest candidate
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the best solution to uncover hidden flaws or missed nuances
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use that reflection to guide a new, refined solution — this is the core of the "Reflect and Regenerate" logic
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the best solution: {reflection}. "
                        f"Re-solve the problem with improved clarity, deeper analysis, and correction of any overlooked aspects."
        )

        return final_solution
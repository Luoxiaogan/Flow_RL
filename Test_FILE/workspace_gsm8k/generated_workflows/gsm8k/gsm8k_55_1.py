# Workflow ID: gsm8k_55_1
# Benchmark: gsm8k
# Data Indices: [846, 469]

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
        This workflow uses a parallel ensemble strategy with minimal steps.
        It generates three independent solutions using the FlexibleCustom operator in 'parallel' mode,
        then selects the best one using ScEnsemble — efficient, robust, and distinct from iterative reflection.
        """
        # Step 1: Generate multiple solutions in parallel using FlexibleCustom
        solution_list = []
        for _ in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem by applying clear, step-by-step reasoning.",
                reasoning_pattern="parallel",
                steps=["identify", "apply", "compute", "validate"]
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the pool
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution
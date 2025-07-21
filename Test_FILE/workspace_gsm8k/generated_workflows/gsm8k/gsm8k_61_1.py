# Workflow ID: gsm8k_61_1
# Benchmark: gsm8k
# Data Indices: [576, 283, 18]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three independent solutions using flexible custom with different reasoning strategies,
        then uses ScEnsemble to select the most accurate one. This approach increases robustness
        by leveraging multiple perspectives without overcomplicating the logic.
        """
        # Step 1: Generate multiple solutions using parallel reasoning patterns
        solutions = []
        for i in range(3):
            # Each solution uses a different reasoning strategy via FlexibleCustom
            solution = await self.flexible_custom(
                custom_instruction="Solve this problem using a clear, step-by-step method.",
                reasoning_pattern="sequential" if i == 0 else "iterative" if i == 1 else "branching",
                steps=["identify", "analyze", "solve", "verify"]
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution from the parallel set
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution
# Workflow ID: gsm8k_336_1
# Benchmark: gsm8k
# Data Indices: [383, 931]

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
        It generates multiple independent solutions in parallel (via a loop), then selects the best one.
        This approach improves robustness by leveraging diverse reasoning paths without requiring iterative refinement or reflection.
        """
        # Step 1: Generate multiple candidate solutions using independent reasoning paths
        solutions = []
        for i in range(3):  # Generate 3 different approaches
            solution = await self.flexible_custom(
                custom_instruction="Solve this problem step-by-step, focusing on clear logic and accurate arithmetic.",
                reasoning_pattern="sequential",
                steps=["understand", "break_down", "calculate", "verify"]
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate solution from the pool
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution
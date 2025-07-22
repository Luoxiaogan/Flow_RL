# Workflow ID: gsm8k_9_1
# Benchmark: gsm8k
# Data Indices: [269, 410]

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
        It generates multiple independent solutions in parallel (via loop), then selects the best one.
        This approach improves robustness by avoiding reliance on a single reasoning path.
        """
        # Step 1: Generate multiple candidate solutions using independent reasoning paths
        solutions = []
        for _ in range(3):  # Generate 3 different approaches
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem using a clear, step-by-step method.",
                reasoning_pattern="sequential",
                steps=["identify", "analyze", "calculate", "verify"]
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the candidates
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
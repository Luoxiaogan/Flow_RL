# Workflow ID: gsm8k_331_1
# Benchmark: gsm8k
# Data Indices: [727, 990, 339]

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
        This workflow uses a parallel ensemble strategy with early filtering.
        It generates multiple candidate solutions in parallel using FlexibleCustom
        with a 'parallel' reasoning pattern, then selects the best one using ScEnsemble.
        This approach is efficient because it avoids iterative refinement and instead
        leverages diversity of initial approaches to find the correct answer faster.
        """
        # Step 1: Generate multiple independent solutions using a parallel reasoning pattern
        solutions = []
        for _ in range(3):  # Generate 3 diverse attempts
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem step-by-step using a different reasoning approach each time.",
                reasoning_pattern="parallel",
                steps=["understand", "break_down", "solve"],
                use_structured_output=True
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate solution from the pool
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution
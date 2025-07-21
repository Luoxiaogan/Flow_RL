# Workflow ID: gsm8k_119_1
# Benchmark: gsm8k
# Data Indices: [566, 298, 466]

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
        This workflow combines two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in): Generate 3 independent solutions to reduce single-point failure.
        2. Reflect and Regenerate: Critically reflect on the best solution, then regenerate a refined version based on that reflection.

        This hybrid approach leverages diversity in initial reasoning and meta-cognition for improvement.
        """
        # Step 1: Generate multiple independent solutions using parallel ensemble
        solutions = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step using a unique method each time. "
                            "First, identify what is given and what must be found. Then, apply relevant formulas or logic. "
                            "Finally, verify your answer with an alternative approach if possible."
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate solution from the pool
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected best solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the best solution: {reflection}. "
                        "Now, provide a revised solution that addresses any overlooked assumptions, errors, or inefficiencies identified in the reflection."
        )

        return final_solution
# Workflow ID: gsm8k_62_0
# Benchmark: gsm8k
# Data Indices: [863, 722]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates three independent solutions with different reasoning strategies,
        then selects the most consistent one via ensemble, followed by a final review.
        """
        # Step 1: Generate multiple solutions using varied approaches (Parallel Ensemble)
        solutions = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Direct calculation with clear steps
                instruction = "Solve the problem step-by-step. First, identify known quantities, then apply arithmetic operations logically."
            elif i == 1:
                # Strategy 2: Use structured decomposition
                instruction = "Break the problem into smaller sub-problems. Solve each systematically, then combine results."
            else:
                # Strategy 3: Assume a solution and verify it
                instruction = "Start by making an educated guess. Then, validate your answer using the original conditions."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution based on consistency
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish the chosen solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
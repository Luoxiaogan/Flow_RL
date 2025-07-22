# Workflow ID: gsm8k_289_1
# Benchmark: gsm8k
# Data Indices: [638, 35, 997]

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
        It generates three independent solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. Finally, it performs a
        single review to polish the selected solution — ensuring robustness and accuracy.
        This approach avoids over-reliance on any single reasoning path and leverages
        diversity to reduce error risk.
        """
        # Step 1: Generate three distinct solutions using varied prompts (parallel ensemble)
        solutions = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem by first identifying all numerical relationships explicitly. Then apply operations step-by-step."
            elif i == 1:
                instruction = "Break the problem into sub-problems and solve each one independently before combining results."
            else:
                instruction = "Use a structured approach: define knowns, unknowns, and constraints; then derive the answer logically."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final refinement via Review to improve clarity, correctness, or completeness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
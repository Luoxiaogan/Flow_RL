# Workflow ID: gsm8k_329_1
# Benchmark: gsm8k
# Data Indices: [187, 747]

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
        It generates three independent solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. Finally, it applies a review
        to polish the chosen solution — ensuring both diversity and quality.
        """
        # Step 1: Generate multiple candidate solutions in parallel using varied instructions
        solution_pool = []
        for i in range(3):
            if i == 0:
                instruction = "Break down the problem into clear numerical components first, then compute each step-by-step."
            elif i == 1:
                instruction = "Solve by identifying all cost categories explicitly, calculating each total separately, and summing them up."
            else:
                instruction = "Use structured reasoning: list known values, apply formulas per category, then combine results."

            solution = await self.custom(instruction=instruction)
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Apply final review to improve clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
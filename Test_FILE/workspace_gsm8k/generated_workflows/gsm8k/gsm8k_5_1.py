# Workflow ID: gsm8k_5_1
# Benchmark: gsm8k
# Data Indices: [78, 826, 506]

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
        It generates three independent solutions with varied reasoning strategies,
        then selects the most consistent one using ScEnsemble. A final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple candidate solutions using different reasoning approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem step-by-step using a clear, linear approach."
            elif i == 1:
                instruction = "Break down the problem into smaller sub-problems and solve each systematically."
            else:
                instruction = "Use an estimation-first strategy: approximate key values before computing exactly."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement via review to ensure clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
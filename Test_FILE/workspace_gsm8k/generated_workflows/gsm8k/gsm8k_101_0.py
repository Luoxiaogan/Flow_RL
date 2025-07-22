# Workflow ID: gsm8k_101_0
# Benchmark: gsm8k
# Data Indices: [305, 252]

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
        Generates 3 independent solutions with different reasoning strategies,
        then ensembles them for improved accuracy. Final review ensures clarity.
        """
        # --- PARALLEL ENSEMBLE: Generate 3 distinct solutions ---
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by identifying patterns in sequences or series."
            elif i == 1:
                instruction = "Break down the problem into daily increments and sum them systematically."
            else:
                instruction = "Model this as an arithmetic progression and apply the standard formula."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- ENSEMBLE: Select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- FINAL REVIEW: Improve clarity and correctness of the best solution ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
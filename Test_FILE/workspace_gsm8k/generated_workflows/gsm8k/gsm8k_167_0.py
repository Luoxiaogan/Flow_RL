# Workflow ID: gsm8k_167_0
# Benchmark: gsm8k
# Data Indices: [765, 337, 986]

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
        It generates 3 independent solutions with different reasoning strategies,
        then selects the best one via ScEnsemble. Finally, it performs a final review
        to ensure clarity and correctness — enhancing robustness without overfitting.
        """

        # --- Step 1: Generate multiple diverse solutions using parallel ensemble ---
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve this math problem by breaking it into clear, logical steps. Show all calculations explicitly."
            elif i == 1:
                instruction = "Think like a teacher explaining this step-by-step to a student. Use plain language and emphasize how each part connects."
            else:
                instruction = "Use dimensional analysis or unit conversion logic to solve this systematically — track units at every stage."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review to polish clarity, fix potential oversights, and improve readability ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
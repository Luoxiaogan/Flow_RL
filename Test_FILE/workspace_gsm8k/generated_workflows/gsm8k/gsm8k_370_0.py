# Workflow ID: gsm8k_370_0
# Benchmark: gsm8k
# Data Indices: [409, 814]

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
        Generates 3 different solutions via varied instructions, ensembles them,
        then applies a final review for consistency and clarity.
        """
        # --- Step 1: Generate 3 independent solutions using different reasoning strategies ---
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step using arithmetic operations only. Break down each part clearly."
            elif i == 1:
                instruction = "Use a table or list to track all transactions and values. Then compute the final amount."
            else:
                instruction = "Think like a financial planner: identify income, expenses, and savings first, then calculate remaining balance."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to select the best solution based on internal consistency ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review to polish clarity and fix any subtle errors ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
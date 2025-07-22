# Workflow ID: gsm8k_15_1
# Benchmark: gsm8k
# Data Indices: [656, 196, 879]

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
        It generates three independent solutions with different reasoning strategies,
        then selects the most consistent one using ScEnsemble. A final review ensures clarity.
        """
        # Step 1: Generate multiple candidate solutions using varied approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem by first identifying all numerical changes step-by-step."
            elif i == 1:
                instruction = "Break the problem into parts and solve each part independently before combining."
            else:
                instruction = "Use a table or list to track each transaction (return/check-out) as it happens."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement — review the selected solution for clarity and correctness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
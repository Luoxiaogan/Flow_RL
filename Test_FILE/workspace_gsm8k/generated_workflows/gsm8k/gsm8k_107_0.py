# Workflow ID: gsm8k_107_0
# Benchmark: gsm8k
# Data Indices: [803, 83, 418]

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
        Generates 3 independent solutions via different reasoning strategies,
        then selects the best one using ScEnsemble. A final review ensures clarity.
        """

        # Step 1: Generate multiple candidate solutions using varied approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by defining variables for each unknown quantity and setting up equations."
            elif i == 1:
                instruction = "Break the problem into smaller logical chunks: identify relationships, build a system, and solve iteratively."
            else:
                instruction = "Use a trial-and-error method: assume values for one variable, check consistency, adjust until the total matches."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review to polish and clarify the selected solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
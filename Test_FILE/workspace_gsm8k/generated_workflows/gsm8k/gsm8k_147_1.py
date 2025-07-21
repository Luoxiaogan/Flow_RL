# Workflow ID: gsm8k_147_1
# Benchmark: gsm8k
# Data Indices: [372, 264, 429]

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
        then uses ScEnsemble to select the most consistent and accurate one.
        A final review ensures clarity and correctness before returning the result.
        """
        # Step 1: Generate multiple candidate solutions using varied reasoning approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by first identifying all costs and revenues separately, then compute profit."
            elif i == 1:
                instruction = "Break the problem into smaller sub-problems (e.g., apples, oranges), solve each independently, then combine."
            else:
                instruction = "Use a structured approach: define variables, write equations, and solve systematically."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ensemble to pick the best solution based on internal consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution for clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
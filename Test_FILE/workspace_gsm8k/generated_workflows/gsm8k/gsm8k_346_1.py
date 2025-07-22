# Workflow ID: gsm8k_346_1
# Benchmark: gsm8k
# Data Indices: [503, 603, 605]

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
        This is a diverse workflow using the 'Parallel Ensemble' pattern.
        It generates three distinct solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. A final review ensures clarity and correctness.
        This approach improves robustness by leveraging multiple perspectives — a fundamentally different logic from the Reflect-and-Regenerate pattern.
        """

        # Step 1: Generate 3 independent solutions using varied prompts to encourage diverse reasoning paths
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem step-by-step using arithmetic reasoning. Focus on identifying patterns or sequences."
            elif i == 1:
                instruction = "Break down the problem into smaller parts. Use logical deduction rather than formulas."
            else:
                instruction = "Use a visual or intuitive method to solve this — imagine it as a real-world scenario."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution for clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
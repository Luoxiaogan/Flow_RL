# Workflow ID: gsm8k_349_0
# Benchmark: gsm8k
# Data Indices: [45, 205, 614]

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
        It generates 3 different solutions via varied instructions, then selects the best one.
        A final review ensures clarity and correctness.
        """
        # --- Generate 3 diverse solutions using different reasoning approaches ---
        solutions = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step: identify what is given, what needs to be found, and apply arithmetic operations logically."
            elif i == 1:
                instruction = "Break the problem into smaller sub-problems. Solve each part independently before combining the results."
            else:
                instruction = "Think like a math tutor: explain your reasoning as if teaching someone who is learning this type of problem for the first time."

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # --- Use ScEnsemble to pick the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Final Review for polish and clarity ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
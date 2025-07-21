# Workflow ID: gsm8k_157_1
# Benchmark: gsm8k
# Data Indices: [28, 543, 877]

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
        Robust parallel ensemble workflow: generate 3 diverse solutions using different reasoning strategies,
        then select the best one with ScEnsemble. Final review ensures clarity and correctness.
        This approach improves reliability by leveraging multiple perspectives and reducing reliance on a single path.
        """
        # Step 1: Generate 3 independent solutions using varied prompts to encourage diverse reasoning paths
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem step-by-step, focusing on identifying all known quantities first before performing any calculations."
            elif i == 1:
                instruction = "Break down the problem into smaller sub-problems. Solve each sub-problem independently, then combine the results logically."
            else:
                instruction = "Think like a teacher: explain your reasoning as if instructing someone who is learning this type of math for the first time."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution — improve clarity, fix potential errors missed during ensembling
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
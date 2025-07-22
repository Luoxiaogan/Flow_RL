# Workflow ID: gsm8k_38_0
# Benchmark: gsm8k
# Data Indices: [811, 63, 18]

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
        Generates 3 distinct solutions via varied instructions, then selects the best one.
        A final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple independent solutions using different reasoning strategies
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Break the problem into clear steps. Identify all distances and calculate total travel distance logically."
            elif i == 1:
                instruction = "Solve this by drawing a simple diagram of the path Talia takes. Then compute the total miles driven."
            else:
                instruction = "Use systematic elimination: list every segment of the journey, sum them up, and double-check your arithmetic."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review to polish and ensure clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
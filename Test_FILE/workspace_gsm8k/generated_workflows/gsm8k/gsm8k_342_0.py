# Workflow ID: gsm8k_342_0
# Benchmark: gsm8k
# Data Indices: [888, 239, 872]

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
        # Step 1: Generate 3 different solutions using parallel ensemble approach
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem by breaking it into clear steps and showing all calculations."
            elif i == 1:
                instruction = "Think like a math teacher: explain each step as if teaching someone new to the topic."
            else:
                instruction = "Use dimensional analysis or unit conversion logic to ensure accuracy in your reasoning."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review to polish the answer
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
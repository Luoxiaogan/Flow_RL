# Workflow ID: gsm8k_252_0
# Benchmark: gsm8k
# Data Indices: [245, 835]

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
        Generates 3 different solutions via varied instructions, then selects the best one.
        Final review ensures clarity and correctness.
        """
        solution_list = []

        # Generate 3 distinct solutions using different reasoning styles
        for i in range(3):
            if i == 0:
                instruction = "Solve this math word problem by first identifying all quantities and their relationships. Then apply arithmetic operations step-by-step."
            elif i == 1:
                instruction = "Break the problem into smaller sub-problems. Solve each one independently, then combine the results logically."
            else:
                instruction = "Use a systematic approach: define variables, write equations based on given information, and solve them methodically."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Enforce consistency via ensemble selection
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Optional but recommended: Final review to polish the answer
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
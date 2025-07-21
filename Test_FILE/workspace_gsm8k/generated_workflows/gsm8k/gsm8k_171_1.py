# Workflow ID: gsm8k_171_1
# Benchmark: gsm8k
# Data Indices: [147, 459, 535]

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
        This is a diverse and effective workflow using the Parallel Ensemble pattern.
        It generates three independent solutions with different reasoning strategies,
        then uses ScEnsemble to select the most consistent one. A final review ensures clarity.
        """
        # Step 1: Generate multiple solutions using varied instructions (parallel ensemble)
        solution_list = []
        for i in range(3):
            instruction = ""
            if i == 0:
                instruction = "Break the problem into clear steps and solve each one methodically."
            elif i == 1:
                instruction = "First identify all quantities, then compute their relationships step by step."
            else:
                instruction = "Solve this as if you're teaching someone who is learning math for the first time."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement — improve clarity and correctness of the selected solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
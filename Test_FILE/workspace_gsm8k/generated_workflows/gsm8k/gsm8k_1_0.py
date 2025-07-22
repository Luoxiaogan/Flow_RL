# Workflow ID: gsm8k_1_0
# Benchmark: gsm8k
# Data Indices: [318, 497, 861]

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
        Generates 3 independent solutions via varied reasoning instructions,
        then selects the best one using ScEnsemble. Final review ensures clarity.
        """
        # Step 1: Generate 3 different solutions using parallel approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve this math word problem by first identifying all quantities and relationships, then setting up equations step-by-step."
            elif i == 1:
                instruction = "Break down the problem into smaller parts: identify what's given, what needs to be found, and how they relate. Solve each part logically."
            else:
                instruction = "Use a visual or tabular method to represent the problem—like drawing boxes for shares or making a table of values—to guide your calculation."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review for clarity, completeness, and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
# Workflow ID: gsm8k_282_0
# Benchmark: gsm8k
# Data Indices: [574, 119]

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
        self.reflect = operator.Reflect(self.config, self.problem) # New operator
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem) # Flexible custom operator

    async def run_workflow(self):
        """
        This is a robust, diverse workflow using the Parallel Ensemble pattern.
        Generates 3 distinct solutions via varied reasoning strategies, then selects the best.
        Final review ensures clarity and correctness.
        """
        # --- PARALLEL ENSEMBLE: Generate 3 different solutions ---
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by identifying each item's cost separately, then summing them."
            elif i == 1:
                instruction = "Break the problem into parts: calculate total cost per category first, then combine."
            else:
                instruction = "Use a structured approach: list known values, apply arithmetic operations, verify each step."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- SCENSEMBLE: Select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- FINAL REVIEW: Improve clarity and catch any remaining errors ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
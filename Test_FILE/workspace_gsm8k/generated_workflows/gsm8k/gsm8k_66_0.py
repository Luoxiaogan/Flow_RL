# Workflow ID: gsm8k_66_0
# Benchmark: gsm8k
# Data Indices: [127, 834]

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
        Generates 3 different solutions with varied reasoning approaches, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # --- STEP 1: Generate 3 independent solutions using different strategies ---
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step using arithmetic operations only. Break down each part of the problem clearly."
            elif i == 1:
                instruction = "Use algebraic modeling: define variables, set up equations, and solve systematically."
            else:
                instruction = "Apply dimensional analysis or unit-based reasoning to ensure all quantities are handled correctly."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- STEP 2: Use ScEnsemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final Review to polish and improve the selected solution ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
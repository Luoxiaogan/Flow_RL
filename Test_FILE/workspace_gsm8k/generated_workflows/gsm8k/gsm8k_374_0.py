# Workflow ID: gsm8k_374_0
# Benchmark: gsm8k
# Data Indices: [517, 241]

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
        Generates 3 distinct solutions via varied instructions, then ensembles them.
        A final review ensures clarity and correctness.
        """
        # --- STEP 1: Generate multiple independent solutions (Parallel Ensemble) ---
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Break down the problem into clear steps. First identify what needs to be added, then perform the addition."
            elif i == 1:
                instruction = "Solve this as if you were teaching someone who just learned about addition of quantities. Be explicit in each step."
            else:
                instruction = "Use a structured approach: list all inputs, sum them up, and verify the total makes sense."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- STEP 2: Use ScEnsemble to pick the best solution based on consistency and clarity ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final Review to polish the selected solution ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
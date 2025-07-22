# Workflow ID: gsm8k_21_0
# Benchmark: gsm8k
# Data Indices: [381, 472, 444]

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
        It generates 3 independent solutions with different reasoning styles,
        then selects the best one via ScEnsemble, followed by a final review for polish.
        """
        # --- Step 1: Generate multiple solutions using varied strategies ---
        solution_list = []
        instructions = [
            "Solve this step-by-step, focusing on breaking down the problem into its components.",
            "First identify all quantities involved, then compute the total sum, then divide by the number of items to get the average.",
            "Use a structured approach: define variables, write equations, solve systematically."
        ]

        for i in range(3):
            solution = await self.custom(instruction=instructions[i])
            solution_list.append(solution)

        # --- Step 2: Use ScEnsemble to pick the most accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final refinement via Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
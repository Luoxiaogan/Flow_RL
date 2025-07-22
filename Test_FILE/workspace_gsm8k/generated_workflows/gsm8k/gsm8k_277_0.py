# Workflow ID: gsm8k_277_0
# Benchmark: gsm8k
# Data Indices: [583, 74]

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
        Diverse and robust workflow using Parallel Ensemble pattern with iterative refinement.
        Generates 3 different solutions via varied reasoning strategies, then selects the best.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple independent solutions using different approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by identifying all quantities first, then applying arithmetic operations."
            elif i == 1:
                instruction = "Break down the problem into parts: define variables for each hall, then compute total."
            else:
                instruction = "Use a visual or table-based approach to track relationships between halls before calculating totals."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review for clarity and correctness (optional but recommended for robustness)
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
# Workflow ID: gsm8k_82_0
# Benchmark: gsm8k
# Data Indices: [283, 179]

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
        This is a robust, diverse workflow using the Parallel Ensemble pattern.
        Generates 3 independent solutions via varied custom instructions,
        then selects the best one using ScEnsemble. A final review ensures polish.
        """
        # Step 1: Generate 3 diverse solutions using different reasoning styles
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by identifying all values and operations needed."
            elif i == 1:
                instruction = "Break the problem into parts: first find what's given, then compute totals."
            else:
                instruction = "Use a structured approach: list knowns, unknowns, and apply formulas logically."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement via Review for clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
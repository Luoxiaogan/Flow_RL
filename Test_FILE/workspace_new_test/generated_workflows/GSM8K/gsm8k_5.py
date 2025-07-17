# Benchmark: GSM8K
# Workflow ID: gsm8k_5
# Data Indices: [80, 81, 82]
# Generation Time: 2025-07-17 22:42:07
# Status: generated
# ==================================================

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
        self.reflect = operator.Reflect(self.config, self.problem)  # New operator

    async def run_workflow(self):
        """
        This is a workflow graph using the Parallel Ensemble pattern with diverse solution generation and final review.
        """
        solution_list = []

        # Generate 3 different solutions using varied instructions
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem step-by-step, breaking down each operation clearly."
            elif i == 1:
                instruction = "Approach the problem by first identifying all quantities and operations involved."
            else:
                instruction = "Use a structured method to solve the problem, showing all calculations explicitly."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Use ScEnsemble to select the most consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Optionally refine the best solution with a Review
        refined_solution = await self.review(pre_solution=best_solution)

        return refined_solution
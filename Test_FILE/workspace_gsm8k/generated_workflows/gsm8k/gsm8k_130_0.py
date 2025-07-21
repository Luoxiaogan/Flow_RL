# Workflow ID: gsm8k_130_0
# Benchmark: gsm8k
# Data Indices: [635, 781, 773]

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
        Generates 3 different solutions via varied reasoning instructions,
        then selects the best one with ScEnsemble. Final review ensures clarity.
        """
        solution_list = []

        # Generate three distinct solutions using different strategies
        for i in range(3):
            if i == 0:
                instruction = "Break the problem into clear steps: identify knowns, unknowns, and relationships."
            elif i == 1:
                instruction = "Solve this by first writing down all relevant equations or formulas that apply."
            else:
                instruction = "Approach this as if you're teaching someone who has never seen this type of problem before."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Final refinement step for clarity and correctness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
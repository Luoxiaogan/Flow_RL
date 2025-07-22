# Workflow ID: gsm8k_320_1
# Benchmark: gsm8k
# Data Indices: [668, 287]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Diverse and robust workflow using Parallel Ensemble + Final Review.
        This pattern generates 3 distinct solutions via varied reasoning strategies (step-by-step, formula-first, and estimation-based),
        then uses ScEnsemble to select the most consistent answer — a fundamentally different approach from iterative refinement or reflection.
        """
        # Step 1: Generate multiple independent solutions using diverse instructions
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve step-by-step by breaking down the problem into smaller parts."
            elif i == 1:
                instruction = "First identify the key formulas or relationships needed, then apply them systematically."
            else:
                instruction = "Start with an estimation or intuitive guess, then refine it using logical reasoning."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on consistency and clarity
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution — ensures no hidden flaws remain
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
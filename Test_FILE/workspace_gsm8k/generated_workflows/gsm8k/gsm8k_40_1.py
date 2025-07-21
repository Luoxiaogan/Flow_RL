# Workflow ID: gsm8k_40_1
# Benchmark: gsm8k
# Data Indices: [673, 713]

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
        This is a diverse workflow using the 'Parallel Ensemble' pattern.
        It generates three independent solutions with different reasoning strategies,
        then selects the most consistent one via ScEnsemble. Finally, it applies a
        light review to polish the final answer.
        """
        # Step 1: Generate multiple candidate solutions using varied instructions
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve the problem by first converting all units to a common measure (e.g., teaspoons), then calculate percentages step-by-step."
            elif i == 1:
                instruction = "Break the problem into parts: identify each ingredient's contribution, sum total volume, and compute percentage as (part/whole)*100."
            else:
                instruction = "Use a structured approach: list knowns, unknowns, apply relevant formulas, and verify consistency before concluding."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Apply a final review to refine clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
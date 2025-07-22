# Workflow ID: gsm8k_191_1
# Benchmark: gsm8k
# Data Indices: [289, 571]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates 3 distinct solutions with different reasoning strategies,
        then selects the most consistent one via ScEnsemble. Finally, it applies
        a single review to polish the final answer — ensuring both diversity and refinement.
        """
        # Step 1: Generate multiple independent solutions using varied approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                instruction = "Solve this math problem by first identifying all given quantities, then applying step-by-step arithmetic operations."
            elif i == 1:
                instruction = "Break the problem into logical subparts. Solve each part separately before combining the results."
            else:
                instruction = "Use a structured approach: define variables, write equations, solve them, and verify the answer."

            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to improve clarity or catch any remaining issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
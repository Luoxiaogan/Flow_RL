# Workflow ID: gsm8k_193_1
# Benchmark: gsm8k
# Data Indices: [107, 981, 266]

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
        This workflow uses the Parallel Ensemble pattern for robustness.
        It generates three diverse initial solutions using different reasoning strategies,
        then selects the most consistent one via ScEnsemble. A final Review step ensures clarity and correctness.
        """
        # Step 1: Generate multiple independent solutions using varied approaches
        solution_list = []
        instructions = [
            "Solve by identifying all given quantities, defining the required calculation, and computing the result step-by-step.",
            "Break the problem into smaller sub-problems, solve each independently, then combine the results logically.",
            "Use a structured approach: first define variables, then write equations, and finally compute the answer."
        ]
        
        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on internal consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final refinement through review to ensure clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
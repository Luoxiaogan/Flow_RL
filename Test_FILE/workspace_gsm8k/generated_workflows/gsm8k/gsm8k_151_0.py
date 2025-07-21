# Workflow ID: gsm8k_151_0
# Benchmark: gsm8k
# Data Indices: [600, 530]

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
        self.reflect = operator.Reflect(self.config, self.problem) # New operator
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem) # Flexible custom operator

    async def run_workflow(self):
        """
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates 3 distinct solutions via varied instructions, then selects the best one.
        A final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple solutions using different reasoning strategies
        solution_list = []
        instructions = [
            "Solve by setting up an equation based on the fractions given.",
            "Break down the problem into steps: first find what fraction was spent on the sweater, then calculate total savings.",
            "Use a visual model (like a bar divided into parts) to represent the savings and derive the total."
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review for clarity and potential improvement
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
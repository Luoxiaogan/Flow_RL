# Workflow ID: gsm8k_311_1
# Benchmark: gsm8k
# Data Indices: [338, 731, 977]

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
        It generates three independent solutions with different reasoning strategies,
        then selects the most consistent one using ScEnsemble. A final review ensures clarity and correctness.
        This approach improves robustness by avoiding reliance on a single reasoning path.
        """

        # Step 1: Generate multiple candidate solutions using varied approaches
        solution_list = []
        instructions = [
            "Solve step-by-step: First identify known quantities, then apply arithmetic operations in order.",
            "Break down the problem into smaller sub-problems, solve each separately, then combine results.",
            "Use visual or numerical modeling: represent the problem as a diagram or equation before solving."
        ]

        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution based on consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish the selected solution—ensure clarity, correctness, and completeness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
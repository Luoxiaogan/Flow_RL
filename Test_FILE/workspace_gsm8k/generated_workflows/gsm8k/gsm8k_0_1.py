# Workflow ID: gsm8k_0_1
# Benchmark: gsm8k
# Data Indices: [1, 6]

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
        # Step 1: Generate three different solutions using varied reasoning approaches
        solution1 = await self.flexible_custom(
            custom_instruction="Solve the problem by first identifying all given values and then applying appropriate operations.",
            reasoning_pattern="sequential",
            steps=["identify_values", "formulate_equation", "compute_result", "validate"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Approach the problem by breaking it into smaller parts and solving each part step-by-step.",
            reasoning_pattern="iterative",
            steps=["divide_into_parts", "solve_each_part", "combine_results"],
            max_iterations=2
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Use a parallel reasoning approach to explore multiple potential methods for solving the problem.",
            reasoning_pattern="parallel",
            steps=["method_1", "method_2", "method_3"]
        )

        # Step 2: Collect all generated solutions into a list
        solutions = [solution1, solution2, solution3]

        # Step 3: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the final solution to ensure clarity and correctness
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution
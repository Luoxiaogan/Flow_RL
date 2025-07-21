# Workflow ID: gsm8k_136_1
# Benchmark: gsm8k
# Data Indices: [864, 341]

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
        It generates three independent solutions using different reasoning approaches,
        then selects the best one via ensemble evaluation — a simple yet effective strategy
        that avoids over-reliance on any single reasoning path.
        """
        # Step 1: Generate multiple diverse solutions using flexible custom with different patterns
        solution1 = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["identify_knowns", "set_up_equations", "solve_step_by_step", "verify"],
            custom_instruction="Solve this math word problem by following a structured step-by-step approach."
        )

        solution2 = await self.flexible_custom(
            reasoning_pattern="parallel",
            steps=["analyze_each_part", "compute_individually", "combine_results"],
            custom_instruction="Break the problem into parts and solve each part independently before combining."
        )

        solution3 = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "final_check"],
            max_iterations=2,
            custom_instruction="Start with an estimate, then refine your answer in two passes."
        )

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        final_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return final_solution
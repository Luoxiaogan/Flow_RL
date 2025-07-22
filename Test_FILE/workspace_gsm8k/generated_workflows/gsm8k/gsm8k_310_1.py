# Workflow ID: gsm8k_310_1
# Benchmark: gsm8k
# Data Indices: [560, 276, 672]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three distinct solutions using different reasoning strategies (sequential, iterative, branching),
        then selects the most consistent one via ScEnsemble. Finally, it applies a review to polish the best result.
        This approach increases robustness by exploring multiple reasoning paths and leveraging consensus.
        """

        # Step 1: Generate three independent solutions using different FlexibleCustom configurations
        solution1 = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem into clear, sequential steps."
        )

        solution2 = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2,
            custom_instruction="Start with an estimate, then refine your answer in two passes."
        )

        solution3 = await self.flexible_custom(
            reasoning_pattern="branching",
            steps=["identify_assumptions", "explore_alternatives", "choose_best_path"],
            custom_instruction="Consider multiple possible interpretations or methods for solving this."
        )

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        ensemble_result = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Final refinement using Review to improve clarity and correctness
        final_solution = await self.review(pre_solution=ensemble_result)

        return final_solution
# Workflow ID: gsm8k_62_0
# Benchmark: gsm8k
# Data Indices: [992, 418, 540]

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
        Generates 3 different solutions via varied reasoning strategies, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Use a step-by-step breakdown of the problem into known quantities and operations.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "perform_calculation", "verify"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Apply a visual modeling approach: draw or describe how each component contributes to the final result.",
            reasoning_pattern="branching",
            steps=["model_components", "map_interactions", "compute_total", "check_consistency"]
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Solve iteratively: start with an estimate, refine it in two passes, and explain why each step improves accuracy.",
            reasoning_pattern="iterative",
            steps=["initial_estimate", "refine", "final_check"],
            max_iterations=2
        )

        # Step 2: Ensemple the three solutions using ScEnsemble for robustness
        solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish the chosen solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer
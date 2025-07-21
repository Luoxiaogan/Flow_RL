# Workflow ID: gsm8k_153_1
# Benchmark: gsm8k
# Data Indices: [552, 964]

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
        Efficient and diverse workflow using Iterative Refinement with FlexibleCustom.
        1. Use FlexibleCustom in 'iterative' mode to generate an initial solution and refine it in one loop.
        2. This avoids unnecessary parallel generation and ensemble selection, focusing on progressive improvement.
        3. The iterative pattern ensures the model learns from its own reasoning steps — a lightweight yet effective strategy.
        """

        # Step 1: Generate an initial solution with iterative refinement
        refined_solution = await self.flexible_custom(
            custom_instruction="Solve step-by-step and refine your approach iteratively.",
            reasoning_pattern="iterative",
            steps=["analyze", "solve", "review", "improve"],
            max_iterations=2  # Two passes: first solve, then improve
        )

        # Step 2: Final review for polish (optional but adds robustness)
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer
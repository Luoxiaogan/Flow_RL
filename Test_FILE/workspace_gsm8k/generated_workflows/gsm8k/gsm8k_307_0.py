# Workflow ID: gsm8k_307_0
# Benchmark: gsm8k
# Data Indices: [962, 532, 192]

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
        This is a diverse, multi-pattern workflow combining:
        1. Parallel Ensemble (fan-out) to generate multiple initial solutions
        2. Reflect + Regenerate (meta-cognitive loop) to improve the best one
        3. Iterative Refinement using FlexibleCustom for final polish
        """

        # Step 1: Generate 3 independent solutions via parallel ensemble
        solution_pool = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step, explaining each reasoning stage clearly."
            )
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to pick the most promising solution
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect critically on the chosen solution — identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, regenerate with targeted guidance
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        "Now, produce a revised and more robust answer that addresses these concerns."
        )

        # Step 5: Final iterative refinement using FlexibleCustom in 'iterative' mode
        # This allows progressive improvement without starting from scratch
        refined_solution = await self.flexible_custom(
            custom_instruction="Refine the solution through multiple passes, focusing on clarity and correctness.",
            reasoning_pattern="iterative",
            steps=["analyze", "identify_assumptions", "validate", "improve"],
            max_iterations=2
        )

        return refined_solution
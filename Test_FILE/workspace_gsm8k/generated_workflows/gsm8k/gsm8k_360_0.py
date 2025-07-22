# Workflow ID: gsm8k_360_0
# Benchmark: gsm8k
# Data Indices: [840, 898]

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
        This is a diverse and complex workflow combining:
        1. Parallel Ensemble (fan-out) to generate multiple initial solutions
        2. Reflect and Regenerate pattern: critique the best solution and use that reflection to guide a refined answer
        3. Iterative Refinement on the final solution for polish
        """

        # Step 1: Generate 3 independent solutions via parallel ensemble
        solutions = []
        for _ in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step using clear mathematical reasoning. Break it into parts."
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution — identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved Custom call
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the previous solution: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind, ensuring clarity, completeness, and correctness."
        )

        # Step 5: Optional iterative refinement — improve final answer further if needed
        # (This simulates real-world reasoning where even good answers benefit from a second pass)
        refined_final = await self.review(pre_solution=final_answer)

        return refined_final
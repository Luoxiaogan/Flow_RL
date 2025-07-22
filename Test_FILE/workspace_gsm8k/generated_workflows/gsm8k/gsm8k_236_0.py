# Workflow ID: gsm8k_236_0
# Benchmark: gsm8k
# Data Indices: [95, 178]

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
        2. Reflect and Regenerate pattern: Critique the best solution, then use that reflection to guide a new, improved solution
        3. Iterative Refinement on the final solution for robustness
        """

        # Step 1: Generate multiple independent solutions via parallel ensemble
        solution_pool = []
        for _ in range(4):  # Generate 4 different approaches
            sol = await self.custom(
                instruction="Solve this math problem by breaking it into clear steps. Consider alternative interpretations of the problem."
            )
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to pick the most accurate one
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect critically on the best solution — identify potential flaws or missing assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a fresh Custom call for an improved solution
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. Now, solve the problem again with more precision, focusing on addressing these points."
        )

        # Step 5: Optional iterative refinement — apply Review once more to polish the final answer
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer
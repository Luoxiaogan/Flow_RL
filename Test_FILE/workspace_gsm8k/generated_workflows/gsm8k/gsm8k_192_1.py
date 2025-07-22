# Workflow ID: gsm8k_192_1
# Benchmark: gsm8k
# Data Indices: [627, 199]

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
        Efficient reflective workflow: Generate a solution, reflect on it to identify potential flaws,
        then use that reflection to guide a targeted revision — all in one logical loop.
        This is different from the existing workflow because:
          - It uses a meta-cognitive loop (Reflect + Custom) instead of parallel ensembling or iterative review
          - It avoids generating multiple solutions unnecessarily
          - It focuses on single-step improvement guided by deep critique
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each part clearly and logically."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a focused revision
        final_answer = await self.custom(
            instruction=f"Based on the following reflection, improve the solution:\n\n{reflection}\n\nProvide a corrected and more robust answer."
        )

        return final_answer
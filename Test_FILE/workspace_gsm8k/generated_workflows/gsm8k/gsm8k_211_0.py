# Workflow ID: gsm8k_211_0
# Benchmark: gsm8k
# Data Indices: [230, 821, 634]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on its weaknesses or assumptions.
        4. Use that reflection to guide a new solution (regeneration).
        5. Return the final refined answer.
        """
        # Step 1: Generate multiple solutions in parallel
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve this math problem step-by-step, showing all calculations clearly.")
            solutions.append(sol)

        # Step 2: Enforce quality by selecting the best among them
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected solution — not to rewrite it, but to understand potential flaws
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate with insight from reflection — use FlexibleCustom for structured reasoning
        final_instruction = f"Given the initial solution and the following reflection: {reflection}. Now, provide a revised, more accurate solution."
        final_answer = await self.flexible_custom(
            custom_instruction=final_instruction,
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        return final_answer
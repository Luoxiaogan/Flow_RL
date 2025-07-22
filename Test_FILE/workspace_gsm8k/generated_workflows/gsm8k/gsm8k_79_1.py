# Workflow ID: gsm8k_79_1
# Benchmark: gsm8k
# Data Indices: [881, 483, 438]

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
        This workflow uses a hybrid of Parallel Ensemble + Reflect-and-Regenerate.
        It first generates 3 diverse solutions in parallel (fan-out), selects the best one via ScEnsemble,
        then critically reflects on that top solution and regenerates a final answer based on the reflection.
        This combines robustness (from ensemble) with meta-cognitive refinement (from reflection).
        """
        # Step 1: Generate 3 independent solutions using different reasoning styles
        # Each uses a unique prompt to encourage diverse approaches
        solutions = [
            await self.custom(instruction="Solve this step-by-step using arithmetic operations only."),
            await self.custom(instruction="Break down the problem into logical cases or scenarios."),
            await self.custom(instruction="Use algebraic expressions to model the situation.")
        ]

        # Step 2: Use ScEnsemble to pick the most accurate among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution — identify assumptions, potential flaws, or missing steps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a targeted regeneration — no guesswork, just focused improvement
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the best solution: '{reflection}'. "
                        "Now, provide a final, fully refined answer that addresses all concerns raised."
        )

        return final_answer
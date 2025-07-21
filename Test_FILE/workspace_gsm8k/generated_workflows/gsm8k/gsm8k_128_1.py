# Workflow ID: gsm8k_128_1
# Benchmark: gsm8k
# Data Indices: [860, 650]

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
        Diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions (Parallel Ensemble).
        2. Select the best one using ScEnsemble.
        3. Reflect on that solution to uncover hidden assumptions or errors.
        4. Use the reflection to guide a targeted regen of the final answer.
        This approach ensures robustness through diversity and meta-cognition.
        """
        # Step 1: Generate multiple solutions in parallel (fan-out)
        solutions = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Focus on mathematical accuracy and logical clarity."
            )
            solutions.append(sol)

        # Step 2: Choose the best solution via ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the chosen solution (meta-cognition)
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a refined solution based on reflection
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. "
                       "Re-solve the problem again, ensuring all steps are logically sound, mathematically correct, and free from any previously identified flaws. "
                       "Provide a concise yet complete explanation."
        )

        return final_answer
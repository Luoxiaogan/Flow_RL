# Workflow ID: gsm8k_7_0
# Benchmark: gsm8k
# Data Indices: [917, 698]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions via parallel ensemble (robustness).
        2. Select the best one using ScEnsemble.
        3. Reflect on it to identify potential flaws or missed angles.
        4. Use reflection to guide a targeted regenerative step for improved accuracy.
        """
        # --- Step 1: Parallel Ensemble — Generate multiple initial solutions ---
        solution_candidates = []
        for i in range(3):  # Generate 3 different approaches
            candidate = await self.custom(
                instruction="Solve the problem by breaking it into logical steps. Focus on clarity and correctness."
            )
            solution_candidates.append(candidate)

        # --- Step 2: Select the best solution using ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Step 3: Reflect on the selected solution — critical meta-cognition ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate based on reflection — improve with insight ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                       f"Re-solve the problem incorporating this feedback to ensure completeness and accuracy."
        )

        return final_answer
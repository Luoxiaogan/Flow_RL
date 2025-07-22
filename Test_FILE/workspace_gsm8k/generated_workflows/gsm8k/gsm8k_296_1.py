# Workflow ID: gsm8k_296_1
# Benchmark: gsm8k
# Data Indices: [996, 259, 554]

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
        This is a diverse and efficient workflow using the Parallel Ensemble + Reflect-and-Regenerate hybrid pattern.
        It first generates multiple independent solutions (parallel), then selects the best one,
        and finally applies a reflective critique to refine it further — ensuring both robustness and depth.
        This logic differs fundamentally from the existing workflow by introducing parallel exploration before reflection.
        """

        # Step 1: Generate 3 independent solutions using flexible custom with different reasoning patterns
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            solution = await self.flexible_custom(
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                custom_instruction="Solve this problem step-by-step with clear reasoning."
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate of the three initial attempts
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected best solution — identify potential blind spots or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a final answer based on the reflection, incorporating deeper insight
        final_answer = await self.custom(
            instruction=f"Based on the following reflection on the current solution: {reflection}. "
                        "Re-solve the problem with improved rigor, clarity, and attention to edge cases or hidden assumptions."
        )

        return final_answer
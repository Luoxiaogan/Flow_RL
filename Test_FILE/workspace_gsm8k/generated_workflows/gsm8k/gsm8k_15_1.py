# Workflow ID: gsm8k_15_1
# Benchmark: gsm8k
# Data Indices: [425, 804]

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
        This is a diverse and effective workflow combining:
        - Parallel Ensemble (Fan-out/Fan-in) for robustness
        - Reflect and Regenerate to refine the best solution
        - Iterative Refinement via Review to polish the final answer
        
        The flow:
        1. Generate 3 independent solutions using flexible custom (parallel).
        2. Use ScEnsemble to pick the best one.
        3. Reflect on that best solution to identify potential flaws or improvements.
        4. Use the reflection to guide a new, improved solution via Custom.
        5. Finally, review that improved solution to ensure clarity and correctness.
        """

        # Step 1: Generate multiple independent solutions (Parallel Ensemble)
        solutions = []
        for _ in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem step-by-step with clear reasoning.",
                reasoning_pattern="sequential",
                steps=["identify", "plan", "solve", "verify"]
            )
            solutions.append(solution)

        # Step 2: Select the best solution using ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate based on reflection (Reflect + Custom)
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. "
                        f"Generate an improved, more accurate version of this solution."
        )

        # Step 5: Final refinement via Review (Iterative Refinement)
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution
# Workflow ID: gsm8k_71_0
# Benchmark: gsm8k
# Data Indices: [322, 173, 738]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate multiple candidate solutions in parallel (fan-out).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Critically reflect on the best solution to uncover hidden flaws or missed steps.
        Step 4: Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """

        # --- PARALLEL ENSEMBLE: Generate 3 independent solutions ---
        solutions = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve this math problem step-by-step. Break it into logical sub-problems, compute each part carefully, and verify your answer."
            )
            solutions.append(solution)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT ON THE BEST SOLUTION ---
        reflection_text = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE USING REFLECTION TO INFORM A NEW STRATEGY ---
        final_instruction = (
            f"Given the following initial solution:\n{best_solution}\n\n"
            f"And the following reflection on potential issues or improvements:\n{reflection_text}\n\n"
            "Now, solve the problem again using the insights from the reflection. Be more precise, consider edge cases, and ensure all steps are logically sound."
        )

        final_solution = await self.flexible_custom(
            custom_instruction=final_instruction,
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        return final_solution
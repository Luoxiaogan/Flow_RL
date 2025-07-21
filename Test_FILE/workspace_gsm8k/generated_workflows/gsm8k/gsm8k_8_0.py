# Workflow ID: gsm8k_8_0
# Benchmark: gsm8k
# Data Indices: [960, 625]

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
        Step 1: Generate 3 independent solutions using parallel approach (fan-out).
        Step 2: Select the best one via ScEnsemble.
        Step 3: Reflect on that solution to identify potential flaws or missed assumptions.
        Step 4: Use reflection to guide a new, improved Custom solution (fan-in with meta-cognition).
        """
        # --- STEP 1: Parallel Ensemble (Fan-out) ---
        solutions = []
        for i in range(3):  # Generate 3 different reasoning paths
            instruction = f"Generate a unique strategy to solve math word problems. Focus on clarity and step-by-step logic. Avoid assuming anything not given."
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # --- STEP 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection (Reflect-and-Regenerate Pattern) ---
        final_instruction = (
            "Given the initial solution below and the following reflection on its possible weaknesses:\n\n"
            f"{reflection}\n\n"
            "Now, provide a revised and improved solution that addresses the concerns raised in the reflection. "
            "Ensure all steps are logically sound, clearly explained, and free of assumptions."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer
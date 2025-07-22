# Workflow ID: gsm8k_196_0
# Benchmark: gsm8k
# Data Indices: [690, 9]

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
        This is a diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions using FlexibleCustom in parallel mode.
        Step 2: Use ScEnsemble to pick the best one.
        Step 3: Reflect on the best solution to identify potential flaws or missed angles.
        Step 4: Regenerate a new solution based on that reflection — this ensures meta-cognitive improvement.
        """

        # --- STEP 1: Generate multiple initial solutions via Parallel Ensemble ---
        solutions = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem step-by-step with clear reasoning.",
                reasoning_pattern="sequential",
                steps=["understand", "analyze", "solve", "verify"]
            )
            solutions.append(solution)

        # --- STEP 2: Select the best solution from the ensemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect critically on the chosen solution without rewriting it ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate a new solution using the reflection as guidance ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Use this insight to generate a refined, more accurate answer."
        )

        return final_answer
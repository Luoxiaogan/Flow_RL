# Workflow ID: gsm8k_183_0
# Benchmark: gsm8k
# Data Indices: [380, 775]

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
        3. Reflect on its potential flaws or missed assumptions.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom in iterative mode.
        """
        # --- Step 1: Generate multiple candidate solutions (Parallel Ensemble) ---
        candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Avoid making assumptions not supported by the question."
            )
            candidates.append(candidate)

        # --- Step 2: Choose the best among them ---
        best_candidate = await self.sc_ensemble(solutions=candidates)

        # --- Step 3: Reflect critically on the chosen solution ---
        reflection = await self.reflect(pre_solution=best_candidate)

        # --- Step 4: Regenerate a better solution based on reflection ---
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again with improved clarity and rigor.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return final_solution
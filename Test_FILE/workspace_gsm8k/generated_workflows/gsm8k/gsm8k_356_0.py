# Workflow ID: gsm8k_356_0
# Benchmark: gsm8k
# Data Indices: [459, 424, 8]

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
        Step 1: Generate multiple solutions via parallel ensemble (robustness).
        Step 2: Select best solution using ScEnsemble.
        Step 3: Reflect on the selected solution to identify potential flaws or missed logic.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom in iterative mode.
        """

        # --- PARALLEL ENSEMBLE: Generate 3 independent solutions ---
        solutions = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step. Break it into clear logical parts. Be explicit about assumptions."
            )
            solutions.append(sol)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT: Critically analyze the best solution without rewriting it ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE: Use reflection to guide a more refined solution ---
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again with improved clarity, addressing any weaknesses identified.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        return final_solution
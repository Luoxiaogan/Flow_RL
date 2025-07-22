# Workflow ID: gsm8k_98_0
# Benchmark: gsm8k
# Data Indices: [425, 150, 742]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on its weaknesses or assumptions.
        Step 4: Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """

        # --- PARALLEL ENSEMBLE ---
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step. Focus on clarity and logical progression."
            )
            solution_candidates.append(candidate)

        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REFLECT ON BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- USE REFLECTION TO GENERATE A BETTER SOLUTION VIA FLEXIBLECUSTOM (ITERATIVE) ---
        final_solution = await self.flexible_custom(
            custom_instruction="Now, re-solve the problem based on this reflection: " + reflection,
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return final_solution
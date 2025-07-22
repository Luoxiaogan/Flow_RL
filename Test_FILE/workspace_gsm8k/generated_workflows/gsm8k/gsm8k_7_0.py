# Workflow ID: gsm8k_7_0
# Benchmark: gsm8k
# Data Indices: [539, 39, 437]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate multiple candidate solutions via parallel ensemble.
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Critically reflect on it to uncover potential flaws or improvements.
        Step 4: Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Generate multiple independent solutions (Parallel Ensemble) ---
        solutions = []
        for i in range(3):  # Generate 3 different approaches
            sol = await self.custom(instruction="Solve the problem by breaking it into logical steps. Be explicit about units and operations.")
            solutions.append(sol)

        # --- STEP 2: Ensembe the best one ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect critically on the best solution (meta-cognition) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Use reflection to guide a refined solution via FlexibleCustom (Iterative Pattern) ---
        refined_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection: " + reflection,
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "reconstruct_with_insights", "verify_consistency"],
            max_iterations=2
        )

        return refined_solution
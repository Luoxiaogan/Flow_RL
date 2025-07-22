# Workflow ID: gsm8k_315_0
# Benchmark: gsm8k
# Data Indices: [197, 994]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best solution using ScEnsemble.
        3. Critically reflect on the selected solution to uncover hidden flaws or missed assumptions.
        4. Use that reflection to guide a new Custom call for a refined answer.
        This structure mimics human meta-cognition: try multiple approaches, pick the best, then improve it by thinking critically about why it might be flawed.
        """
        # --- Step 1: Generate multiple independent solutions (Parallel Ensemble) ---
        solutions = []
        for _ in range(3):
            solution = await self.custom(instruction="Solve the problem step-by-step, clearly explaining each reasoning phase.")
            solutions.append(solution)

        # --- Step 2: Select the best solution using ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Reflect on the best solution (new operator) ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate with reflection-guided instruction ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a revised, improved solution that addresses any weaknesses or assumptions identified in the reflection."
        )

        return final_answer
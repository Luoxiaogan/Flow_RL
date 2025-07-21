# Workflow ID: gsm8k_178_0
# Benchmark: gsm8k
# Data Indices: [174, 455]

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
        Diverse workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on its weaknesses without rewriting.
        Step 4: Use reflection to guide a new Custom solution that addresses flaws.
        """
        # --- STEP 1: Parallel Ensemble ---
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step with clear reasoning. Focus on breaking down each part independently.")
            solutions.append(sol)

        # --- STEP 2: Ensembling ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection ---
        final_instruction = f"Given the initial solution and this reflection: '{reflection}'. Now, provide a refined solution that addresses potential issues such as assumptions, missing steps, or logical gaps."
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution
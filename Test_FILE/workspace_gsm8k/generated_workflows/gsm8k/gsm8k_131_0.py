# Workflow ID: gsm8k_131_0
# Benchmark: gsm8k
# Data Indices: [436, 24, 789]

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
        2. Select the best one using ScEnsemble.
        3. Reflect on its weaknesses or assumptions.
        4. Use that reflection to guide a new solution generation (not just review).
        This creates a meta-cognitive loop with diversity in both approach and refinement.
        """
        # Step 1: Parallel Ensemble — Generate multiple initial solutions
        solution_pool = []
        for i in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, focusing on clear reasoning. Be creative in your approach—try different strategies if possible.")
            solution_pool.append(sol)

        # Step 2: Ensembling — Pick the strongest candidate
        best_initial = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect — Critically analyze the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Regenerate — Use the reflection to guide a fresh solution
        final_instruction = f"Given the initial solution and the following reflection on potential flaws or missed details: '{reflection}'. Now, provide a refined, improved solution based on this insight."
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution
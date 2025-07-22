# Workflow ID: gsm8k_201_0
# Benchmark: gsm8k
# Data Indices: [52, 575, 617]

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
        1. Generate 3 independent solutions (Parallel Ensemble).
        2. Select the best one using ScEnsemble.
        3. Reflect on it to identify potential flaws or improvements.
        4. Use reflection to guide a new Custom call for final refinement.
        This creates a meta-cognitive loop with ensemble robustness.
        """

        # Step 1: Generate multiple solutions in parallel (Fan-out)
        solution_pool = []
        for i in range(3):
            sol = await self.custom(
                instruction="Solve the problem step-by-step, explaining your reasoning clearly."
            )
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to pick the best initial solution
        best_initial = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect critically on the chosen solution without rewriting it
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Use the reflection to generate a refined solution
        final_answer = await self.custom(
            instruction=f"Given the following initial solution:\n{best_initial}\n\n"
                        f"And the following reflection on its potential weaknesses or improvements:\n{reflection}\n\n"
                        "Now, provide a revised and improved solution based on this analysis."
        )

        return final_answer
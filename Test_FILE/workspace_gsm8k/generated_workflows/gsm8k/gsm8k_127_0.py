# Workflow ID: gsm8k_127_0
# Benchmark: gsm8k
# Data Indices: [538, 405, 592]

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
        1. Generate 3 independent solutions using parallel ensemble.
        2. Select the best solution via ScEnsemble.
        3. Reflect on the best solution to identify potential flaws or improvements.
        4. Use reflection to guide a new Custom call for final refinement.
        """

        # Step 1: Generate multiple candidate solutions in parallel (Parallel Ensemble pattern)
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step by breaking it into clear logical steps. Avoid assumptions; justify each calculation.")
            solutions.append(sol)

        # Step 2: Choose the best among them
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the chosen solution (Reflect operator)
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to generate a final improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution:\n{reflection}\n\nNow, produce a revised and more accurate solution that addresses the identified concerns."
        )

        return final_solution
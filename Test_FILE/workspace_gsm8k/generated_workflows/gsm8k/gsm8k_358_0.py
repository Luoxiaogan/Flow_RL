# Workflow ID: gsm8k_358_0
# Benchmark: gsm8k
# Data Indices: [948, 865]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on it to uncover potential blind spots.
        4. Use that reflection to guide a final refined solution.
        """
        # Step 1: Parallel Ensemble — Generate multiple initial attempts
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem by breaking it into logical steps and checking each step carefully.")
            solutions.append(sol)

        # Step 2: Choose the best solution from the ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the chosen solution — critique assumptions, logic gaps, or ambiguities
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution informed by the reflection
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        "Now, provide a corrected and improved solution based on this insight."
        )

        return final_answer
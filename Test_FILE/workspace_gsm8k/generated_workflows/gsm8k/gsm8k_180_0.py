# Workflow ID: gsm8k_180_0
# Benchmark: gsm8k
# Data Indices: [843, 73, 323]

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
        3. Reflect on it to identify potential flaws or improvements.
        4. Use reflection to guide a final custom solution.
        This creates a robust, meta-cognitive loop that improves accuracy through both diversity and critical analysis.
        """
        # Step 1: Parallel Ensemble — generate multiple initial approaches
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem by breaking it into clear steps. Focus on identifying constraints and resources.")
            solutions.append(sol)

        # Step 2: Select the best solution from the ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critical reflection on the best solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution informed by reflection
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        "Now, synthesize an improved, accurate, and complete answer based on this insight."
        )

        return final_answer
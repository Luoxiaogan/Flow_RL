# Workflow ID: gsm8k_135_1
# Benchmark: gsm8k
# Data Indices: [900, 336, 932]

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
        This is a diverse workflow combining:
        1. Parallel Ensemble (Fan-out) to generate multiple solutions
        2. Reflect and Regenerate pattern to improve the best solution
        3. Iterative refinement on the final solution for robustness
        
        The structure ensures diversity in initial reasoning, critical reflection, and iterative improvement.
        """
        # Step 1: Generate 3 independent solutions using parallel ensemble approach
        solutions = []
        for _ in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step, breaking it into logical parts. Be thorough and explicit."
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the selected solution — identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new Custom call that improves the solution based on insights
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. Now, re-solve the problem with improved clarity and correctness, addressing all identified weaknesses."
        )

        # Step 5: Apply one round of Review to polish the improved solution
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution
# Workflow ID: gsm8k_81_0
# Benchmark: gsm8k
# Data Indices: [762, 59, 735]

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
        This is a diverse and complex workflow combining:
        - Parallel Ensemble (Fan-out/Fan-in) to generate multiple initial solutions
        - Reflect and Regenerate pattern to critique the best solution and improve it
        - Iterative Refinement for final polishing
        """

        # Step 1: Generate 3 independent solutions using parallel ensemble
        solution_list = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step with clear reasoning. Do not rush.")
            solution_list.append(sol)

        # Step 2: Use ScEnsemble to pick the best among them
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect on the best solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new Custom call for a refined solution
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be precise and thorough."
        )

        # Step 5: Optional iterative refinement — review the improved solution one more time
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution
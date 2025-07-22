# Workflow ID: gsm8k_26_0
# Benchmark: gsm8k
# Data Indices: [565, 598]

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
        It first generates 3 independent solutions (Parallel Ensemble), selects the best one,
        then reflects on it to uncover hidden assumptions or errors, and finally regenerates
        a new solution informed by that reflection — mimicking human meta-cognition.
        """
        # Step 1: Generate multiple independent solutions using parallel ensemble
        solutions = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step. Focus on clarity and logical progression."
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the best initial solution
        best_initial = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution to identify flaws or missed details
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Use the reflection to guide a fresh, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        "Now, solve the problem again with deeper reasoning, addressing potential issues noted above."
        )

        return final_solution
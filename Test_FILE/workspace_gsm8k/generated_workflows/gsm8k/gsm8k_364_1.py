# Workflow ID: gsm8k_364_1
# Benchmark: gsm8k
# Data Indices: [678, 676, 535]

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
        Diverse and robust workflow using Parallel Ensemble + Reflect-and-Regenerate.
        This approach first generates multiple independent solutions (parallel), selects the best one,
        then uses reflection to guide a targeted regeneration — mimicking how humans refine ideas after peer review.
        """
        # Step 1: Generate 3 different solutions using parallel reasoning
        solution_pool = []
        for _ in range(3):
            sol = await self.flexible_custom(
                custom_instruction="Solve this math problem using a unique strategy each time.",
                reasoning_pattern="parallel",
                steps=["analyze", "model", "compute", "validate"]
            )
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to pick the most promising initial solution
        best_initial = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect on the best solution to uncover hidden flaws or missed cases
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Based on reflection, generate a new solution that specifically addresses the critique
        final_answer = await self.custom(
            instruction=f"Using the following initial solution:\n{best_initial}\n\nAnd this reflection on potential issues:\n{reflection}\n\nProvide a refined, corrected answer that explicitly addresses the concerns raised."
        )

        return final_answer
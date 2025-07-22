# Workflow ID: gsm8k_119_1
# Benchmark: gsm8k
# Data Indices: [541, 936]

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
        Diverse and efficient workflow using Parallel Ensemble followed by Reflect-and-Regenerate.
        This approach generates multiple initial solutions in parallel to capture different reasoning paths,
        then uses reflection to critique the best one and regenerate a more robust final answer.
        It combines two distinct patterns: Parallel Ensemble (fan-out) + Reflect-and-Regenerate (meta-cognitive loop).
        """
        # Step 1: Generate 3 independent solutions via parallel ensemble (fan-out)
        solution_pool = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step. Consider multiple possible interpretations of the scenario.")
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to select the most coherent and accurate solution from the pool
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or logical gaps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a targeted regenration — now with improved awareness
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be explicit about how you're addressing the identified issues."
        )

        return final_answer
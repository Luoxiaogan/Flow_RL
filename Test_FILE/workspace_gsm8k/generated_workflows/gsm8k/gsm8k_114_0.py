# Workflow ID: gsm8k_114_0
# Benchmark: gsm8k
# Data Indices: [215, 507, 350]

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
        This is a diverse and efficient workflow using iterative refinement with reflection.
        It first generates an initial solution, reflects on it to identify potential flaws,
        then uses that insight to generate a final improved solution — all in under 5 steps.
        """
        # Step 1: Generate initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down each part logically."
        )

        # Step 2: Reflect critically on the initial solution without rewriting
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a targeted re-solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial approach: '{reflection}'. "
                        "Now, solve the problem again with improved clarity and correctness."
        )

        return final_solution
# Workflow ID: gsm8k_265_1
# Benchmark: gsm8k
# Data Indices: [561, 673, 662]

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
        This is a diverse and efficient workflow using the Reflect-and-Regenerate pattern.
        It generates an initial solution, reflects on it to uncover potential flaws or improvements,
        then uses that reflection to guide a targeted re-solution. This mimics human meta-cognition
        and avoids unnecessary parallelism or multiple reviews—focusing on depth over breadth.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each calculation clearly."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be precise and avoid prior mistakes."
        )

        return final_answer
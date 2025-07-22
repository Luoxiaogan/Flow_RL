# Workflow ID: gsm8k_150_0
# Benchmark: gsm8k
# Data Indices: [443, 866, 408]

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
        It generates an initial solution, reflects on it to identify potential flaws or missed steps,
        then uses that reflection to guide a new, improved solution — all in a single logical loop.
        """
        # Step 1: Generate initial solution with clear step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into clear, sequential steps. "
                        "Explain each step thoroughly, including any assumptions made."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        "Now, provide a new, improved solution that addresses the identified issues. "
                        "Ensure your reasoning is complete, accurate, and logically sound."
        )

        return final_solution
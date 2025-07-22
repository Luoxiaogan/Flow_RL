# Workflow ID: gsm8k_261_0
# Benchmark: gsm8k
# Data Indices: [959, 374, 371]

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
        It first generates an initial solution, reflects on it to uncover potential flaws or improvements,
        then uses that reflection to guide a new, more refined solution — all in under 5 steps.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(instruction="Solve the problem by breaking it into clear, logical steps. Show each calculation explicitly.")

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a better, guided solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity, accuracy, and structure."
        )

        return final_solution
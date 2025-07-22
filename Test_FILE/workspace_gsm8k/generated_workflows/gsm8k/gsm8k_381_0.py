# Workflow ID: gsm8k_381_0
# Benchmark: gsm8k
# Data Indices: [393, 486]

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
        It leverages the Reflect operator to critique an initial solution, then uses that insight
        to guide a focused re-solution — all in under 5 steps for maximum efficiency.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(instruction="Solve the problem by breaking it down into smaller, manageable steps. Explain each step clearly.")

        # Step 2: Critically reflect on the initial solution to identify potential flaws or oversights
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution that addresses the identified issues
        final_solution = await self.custom(instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity and accuracy.")

        return final_solution
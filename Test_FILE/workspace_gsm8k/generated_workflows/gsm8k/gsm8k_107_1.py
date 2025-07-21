# Workflow ID: gsm8k_107_1
# Benchmark: gsm8k
# Data Indices: [803, 83, 418]

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
        It generates an initial solution, reflects on its potential weaknesses, and uses that insight
        to produce a refined answer — all in just 3 steps. This avoids unnecessary complexity
        while leveraging meta-cognition for improvement.
        """

        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(instruction="Solve the problem by breaking it into logical steps and showing your work clearly.")

        # Step 2: Critically reflect on the solution to identify assumptions or gaps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(instruction=f"Based on the following reflection about the initial solution: '{reflection}'. Now, provide a corrected and more accurate answer.")

        return final_answer
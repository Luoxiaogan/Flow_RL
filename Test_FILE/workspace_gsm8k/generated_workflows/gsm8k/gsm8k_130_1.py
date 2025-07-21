# Workflow ID: gsm8k_130_1
# Benchmark: gsm8k
# Data Indices: [635, 781, 773]

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
        It generates an initial solution, reflects on its potential weaknesses, 
        then uses that reflection to guide a targeted improvement — mimicking human metacognition.
        This avoids unnecessary parallelism or multiple iterations while still being robust.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify all given values and what needs to be found. Then, apply appropriate mathematical operations. Finally, verify your answer."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. Now, provide a corrected and improved version of the solution, ensuring clarity and correctness."
        )

        return final_solution
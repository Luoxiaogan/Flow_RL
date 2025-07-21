# Workflow ID: gsm8k_19_0
# Benchmark: gsm8k
# Data Indices: [644, 246, 385]

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
        It generates an initial solution, reflects on it to identify potential flaws or missing steps,
        then uses that reflection to guide a new, improved solution — all in under 5 steps.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a targeted instruction for a better solution
        improved_instruction = f"Given the following reflection on the initial solution: '{reflection}'. Now, provide a revised and improved answer that addresses the identified issues."

        # Step 4: Generate a refined solution based on the reflection
        final_solution = await self.custom(instruction=improved_instruction)

        return final_solution
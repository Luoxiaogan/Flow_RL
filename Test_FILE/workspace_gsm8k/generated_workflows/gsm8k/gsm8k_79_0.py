# Workflow ID: gsm8k_79_0
# Benchmark: gsm8k
# Data Indices: [881, 483, 438]

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
        It first generates an initial solution, reflects on its potential weaknesses,
        then uses that reflection to guide a targeted improvement — all in under 5 steps.
        """
        # Step 1: Generate initial solution with clear step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into smaller steps. Show your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a focused re-solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        "Now, provide a revised and improved answer with clearer logic and correct reasoning."
        )

        return final_solution
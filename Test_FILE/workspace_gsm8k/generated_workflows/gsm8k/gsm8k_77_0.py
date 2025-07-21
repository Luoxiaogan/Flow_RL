# Workflow ID: gsm8k_77_0
# Benchmark: gsm8k
# Data Indices: [809, 703, 289]

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
        then uses that reflection to guide a targeted revision — ensuring logical depth without unnecessary complexity.
        """
        # Step 1: Generate an initial solution with clear, step-by-step reasoning
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining each calculation clearly.")

        # Step 2: Critically reflect on the solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a revised solution that addresses the critique
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                        "Now, provide a new, improved solution that corrects any issues identified."
        )

        return final_solution
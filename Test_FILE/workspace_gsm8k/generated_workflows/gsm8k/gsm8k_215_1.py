# Workflow ID: gsm8k_215_1
# Benchmark: gsm8k
# Data Indices: [43, 947]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern.
        It first generates an initial solution, then uses reflection to identify potential flaws,
        and finally regenerates a better solution based on that insight — all in a single, efficient loop.
        This avoids unnecessary parallelism or ensembling, focusing instead on meta-cognitive refinement.
        """

        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each calculation clearly."
        )

        # Step 2: Use Reflect to critique the solution — no rewrite yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        f"Re-solve the problem with improved clarity and accuracy. Be explicit about any assumptions or gaps."
        )

        return final_answer
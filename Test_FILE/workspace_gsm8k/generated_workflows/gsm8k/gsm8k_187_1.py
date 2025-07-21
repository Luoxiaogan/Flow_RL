# Workflow ID: gsm8k_187_1
# Benchmark: gsm8k
# Data Indices: [410, 113]

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
        This workflow uses the Reflect and Regenerate pattern for efficient, meta-cognitive refinement.
        1. Generate an initial solution with a clear instruction.
        2. Critically reflect on its potential flaws or assumptions.
        3. Use that reflection to guide a targeted, improved solution.
        This avoids unnecessary parallelism and focuses on intelligent iteration.
        """
        # Step 1: Initial solution using structured reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what is given, then determine what needs to be found, and finally apply appropriate logic or math."
        )

        # Step 2: Reflect on the solution to uncover blind spots
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a refined solution informed by the reflection
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. Now, provide a revised and more accurate answer."
        )

        return final_answer
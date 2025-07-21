# Workflow ID: gsm8k_181_1
# Benchmark: gsm8k
# Data Indices: [595, 428, 272]

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
        Reflect-and-Regenerate Workflow: Generate a solution, reflect on its potential flaws, then use that reflection to guide a targeted improvement.
        This meta-cognitive loop enhances accuracy by addressing blind spots without unnecessary iterations or parallelism.
        """
        # Step 1: Generate an initial solution using a flexible, structured approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem systematically: identify key elements, formulate steps, and compute the answer.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Critically reflect on the solution — identify assumptions, missing logic, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution with explicit attention to the critique
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a revised solution that addresses these points explicitly."
        )

        return final_solution
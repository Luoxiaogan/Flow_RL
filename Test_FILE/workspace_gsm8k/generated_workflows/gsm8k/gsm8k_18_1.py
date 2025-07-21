# Workflow ID: gsm8k_18_1
# Benchmark: gsm8k
# Data Indices: [725, 329, 649]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it to identify flaws or improvements, then use that reflection to guide a new, improved solution.
        This meta-cognitive loop ensures deeper reasoning by explicitly evaluating one's own work before proceeding.
        """
        # Step 1: Generate an initial solution using general step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Clearly state what is given, what needs to be found, and show all calculations."
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, potential errors, or missing logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution with targeted improvements
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a revised solution that addresses these points while maintaining clarity and correctness."
        )

        return final_solution
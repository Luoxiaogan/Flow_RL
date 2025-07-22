# Workflow ID: gsm8k_254_0
# Benchmark: gsm8k
# Data Indices: [308, 490, 249]

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
        It leverages the Reflect operator to guide improvement, avoiding unnecessary complexity.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Critically reflect on the solution to identify potential flaws or omissions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a revised solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now provide a corrected and improved solution."
        )

        return final_solution
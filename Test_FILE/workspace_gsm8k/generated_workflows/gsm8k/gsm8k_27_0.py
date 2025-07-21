# Workflow ID: gsm8k_27_0
# Benchmark: gsm8k
# Data Indices: [638, 430]

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
        It leverages the Reflect operator to guide improvement without overcomplicating the flow.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve step-by-step",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "execute", "verify"]
        )

        # Step 2: Reflect on the solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Now solve the problem again with clearer logic and fewer errors."
        )

        return final_solution
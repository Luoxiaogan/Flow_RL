# Workflow ID: gsm8k_95_0
# Benchmark: gsm8k
# Data Indices: [648, 279]

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
        # Step 1: Generate an initial solution using a structured flexible custom approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem into clear steps: identify knowns, unknowns, apply operations, and verify results."
        )

        # Step 2: Reflect on the initial solution to uncover potential flaws or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution — no need for multiple iterations
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                       f"Re-solve the problem carefully, ensuring all assumptions are valid and calculations are accurate."
        )

        return final_solution
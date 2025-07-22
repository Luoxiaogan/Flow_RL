# Workflow ID: gsm8k_203_0
# Benchmark: gsm8k
# Data Indices: [463, 211, 387]

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
        Efficient and diverse workflow using iterative refinement with reflection.
        This pattern combines critical thinking (Reflect) with targeted improvement (Custom),
        avoiding unnecessary complexity while ensuring robustness through meta-cognition.
        """
        # Step 1: Generate initial solution using structured reasoning
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break the problem into clear steps: identify quantities, unit prices, and compute totals."
        )

        # Step 2: Reflect on the solution to uncover potential flaws or omissions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a focused revision — no need for multiple iterations
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, provide a revised and improved solution that addresses these points."
        )

        return final_solution
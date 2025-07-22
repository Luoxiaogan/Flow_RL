# Workflow ID: gsm8k_273_0
# Benchmark: gsm8k
# Data Indices: [127, 155, 715]

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
        It uses the Reflect operator to critique an initial solution, then guides a new attempt
        based on that reflection — a meta-cognitive loop that improves accuracy without excessive complexity.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem step-by-step and verify each step."
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a focused revision
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now provide a revised solution that addresses these points. Be precise and logical."
        )

        return final_solution
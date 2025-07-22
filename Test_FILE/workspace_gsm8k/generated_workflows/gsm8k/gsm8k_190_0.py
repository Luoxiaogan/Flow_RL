# Workflow ID: gsm8k_190_0
# Benchmark: gsm8k
# Data Indices: [36, 413, 809]

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
        It leverages the Reflect operator to guide a single, targeted improvement pass — 
        combining meta-cognition with minimal overhead for maximum efficiency.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem step-by-step, showing all calculations clearly."
        )

        # Step 2: Critically reflect on the solution to identify potential flaws or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a focused revision — no need for multiple iterations
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Revise the solution to address any gaps or errors while keeping it concise and accurate."
        )

        return final_solution
# Workflow ID: gsm8k_234_0
# Benchmark: gsm8k
# Data Indices: [767, 78]

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
        This is a diverse and efficient workflow using the Reflect-and-Regenerate pattern.
        It generates an initial solution, reflects on its potential weaknesses, then uses that insight to guide a better solution.
        This balances simplicity with meta-cognitive improvement — ideal for efficiency and robustness.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify all costs and benefits. Then, calculate when total cost of owning chickens becomes less than buying eggs."
        )

        # Step 2: Critically reflect on the initial solution to uncover hidden assumptions or gaps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a more precise instruction for a final solution
        final_instruction = (
            "Based on the following reflection:\n"
            f"{reflection}\n\n"
            "Now, solve the problem again with improved clarity and completeness. Ensure all steps are logically sound and no assumptions are left unexamined."
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution
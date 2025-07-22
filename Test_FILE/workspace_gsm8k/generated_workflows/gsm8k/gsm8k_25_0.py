# Workflow ID: gsm8k_25_0
# Benchmark: gsm8k
# Data Indices: [550, 724, 310]

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
        It avoids over-engineering while ensuring logical depth through meta-cognition.
        """
        # Step 1: Generate an initial solution using a structured approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break the problem into clear steps: identify knowns, define relationships, compute, and check for consistency."
        )

        # Step 2: Reflect on the solution to uncover potential blind spots
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a targeted revision
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Revise the solution accordingly, focusing on improving clarity and correctness."
        )

        return final_solution
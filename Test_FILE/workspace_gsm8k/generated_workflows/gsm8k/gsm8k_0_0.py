# Workflow ID: gsm8k_0_0
# Benchmark: gsm8k
# Data Indices: [232, 432]

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
        This is a diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        It generates an initial solution, reflects critically on it, and uses that reflection to produce a superior final answer.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, explaining each reasoning stage clearly.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Reflect on the initial solution — identify potential flaws, assumptions, or missed logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution via Custom operator
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution:\n{reflection}\n\n"
                        f"Re-solve the problem with improved clarity, accuracy, and logical rigor. "
                        f"Ensure all steps are explicitly justified."
        )

        return final_solution
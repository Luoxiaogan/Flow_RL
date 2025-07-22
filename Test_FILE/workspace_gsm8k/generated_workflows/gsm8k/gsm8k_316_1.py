# Workflow ID: gsm8k_316_1
# Benchmark: gsm8k
# Data Indices: [447, 83]

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
        Reflect-and-Regenerate Workflow: Generate a solution, reflect on it to identify weaknesses, then use that reflection to guide a targeted revision.
        This pattern leverages meta-cognition — not just improving the answer, but understanding *why* it might be flawed — leading to more robust and efficient refinement.
        Unlike iterative review, this uses structured insight from reflection to directly inform the next step, reducing unnecessary iterations.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear reasoning.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Critically reflect on the solution — no rewriting yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a focused, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. Now, solve the problem again with improved clarity and accuracy."
        )

        return final_solution
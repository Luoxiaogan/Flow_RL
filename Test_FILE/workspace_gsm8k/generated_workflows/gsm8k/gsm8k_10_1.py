# Workflow ID: gsm8k_10_1
# Benchmark: gsm8k
# Data Indices: [177, 874, 318]

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
        This workflow uses the 'Reflect and Regenerate' pattern — a meta-cognitive loop.
        It first generates an initial solution, then critically reflects on it to uncover potential flaws or oversights,
        and finally uses that reflection to guide a targeted regeneration of the solution.
        This approach mimics how humans improve reasoning by self-questioning and iterative refinement.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step in a clear, logical sequence.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the initial solution:\n\n{reflection}\n\nNow, provide a revised and improved solution. Focus on addressing any weaknesses or ambiguities identified."
        )

        return final_answer
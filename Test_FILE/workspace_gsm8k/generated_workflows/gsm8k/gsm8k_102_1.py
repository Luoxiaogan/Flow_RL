# Workflow ID: gsm8k_102_1
# Benchmark: gsm8k
# Data Indices: [67, 69]

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
        This is a diverse and robust workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it to identify potential flaws,
        and finally uses that reflection to guide a new, improved solution. This meta-cognitive loop
        ensures deeper reasoning than a single pass.
        """

        # Step 1: Generate an initial solution using flexible custom with a sequential strategy
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by following a clear, step-by-step reasoning path.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "calculate", "verify"]
        )

        # Step 2: Critically reflect on the initial solution — do not rewrite it yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a superior final solution
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Now, provide a new, improved solution that addresses the identified weaknesses or assumptions."
        )

        return final_answer
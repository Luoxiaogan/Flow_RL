# Workflow ID: gsm8k_221_0
# Benchmark: gsm8k
# Data Indices: [489, 148]

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
        Efficient and diverse workflow using Reflect + FlexibleCustom in an iterative refinement loop.
        This pattern combines meta-cognition (reflection) with structured reasoning (FlexibleCustom).
        It avoids unnecessary complexity while ensuring robustness through guided improvement.
        """
        # Step 1: Generate initial solution using flexible custom with a sequential reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using logical decomposition.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "calculate", "verify"]
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or missing logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution via a custom instruction
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        "Now, solve the problem again with improved clarity and accuracy."
        )

        return final_solution
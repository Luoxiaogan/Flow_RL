# Workflow ID: gsm8k_245_1
# Benchmark: gsm8k
# Data Indices: [596, 71]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it to uncover flaws or missed assumptions, then use that reflection to guide a new, improved solution.
        This meta-cognitive loop mimics human learning — not just fixing errors but understanding why they occurred.
        """
        # Step 1: Generate an initial solution using structured reasoning (sequential pattern)
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear explanations.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a superior final solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses all identified issues."
        )

        return final_solution
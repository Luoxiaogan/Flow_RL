# Workflow ID: gsm8k_119_0
# Benchmark: gsm8k
# Data Indices: [541, 936]

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
        Diverse and efficient workflow using iterative refinement with a structured reasoning pattern.
        This approach uses FlexibleCustom in iterative mode to systematically improve the solution,
        ensuring robustness without overcomplicating the process — aligning with efficiency goals.
        """
        # Step 1: Use FlexibleCustom with iterative reasoning pattern for structured, progressive improvement
        solution = await self.flexible_custom(
            custom_instruction="Solve step-by-step with clear reasoning.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Review the final iterative solution to catch any lingering errors or ambiguities
        final_solution = await self.review(pre_solution=solution)

        return final_solution
# Workflow ID: gsm8k_326_0
# Benchmark: gsm8k
# Data Indices: [945, 631]

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
        Efficient and diverse workflow using iterative refinement with a flexible custom operator.
        This approach combines structured reasoning (via FlexibleCustom) with reflection to ensure robustness
        while keeping the overall structure simple and effective — just 4 operators total.
        """
        # Step 1: Use FlexibleCustom in iterative mode to systematically solve the problem
        solution = await self.flexible_custom(
            custom_instruction="Solve step-by-step using systematic reasoning.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "compute", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the generated solution to identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=solution)

        # Step 3: Generate a final improved version based on the reflection
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Provide a revised, more accurate solution."
        )

        return final_solution
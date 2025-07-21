# Workflow ID: gsm8k_134_0
# Benchmark: gsm8k
# Data Indices: [701, 68]

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
        Efficient and diverse workflow using iterative refinement with FlexibleCustom.
        This pattern ensures logical progression while avoiding unnecessary complexity.
        """
        # Step 1: Use FlexibleCustom in iterative mode to solve the problem step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically by breaking it into steps.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Review the solution for clarity and correctness
        final_solution = await self.review(pre_solution=solution)

        return final_solution
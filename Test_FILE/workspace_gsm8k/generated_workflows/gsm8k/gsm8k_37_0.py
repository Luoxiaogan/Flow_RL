# Workflow ID: gsm8k_37_0
# Benchmark: gsm8k
# Data Indices: [525, 606]

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
        This is a diverse and efficient workflow using iterative refinement with FlexibleCustom.
        It uses a structured iterative pattern to progressively improve the solution,
        ensuring logical progression without unnecessary complexity.
        """
        # Step 1: Use FlexibleCustom in iterative mode to build a solution step-by-step
        solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Solve the problem systematically by breaking it into clear phases."
        )

        # Step 2: Review the initial solution for clarity and correctness
        refined_solution = await self.review(pre_solution=solution)

        return refined_solution
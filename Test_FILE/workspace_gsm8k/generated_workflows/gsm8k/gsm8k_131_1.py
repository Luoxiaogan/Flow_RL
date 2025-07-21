# Workflow ID: gsm8k_131_1
# Benchmark: gsm8k
# Data Indices: [436, 24, 789]

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
        Efficient and diverse workflow using Iterative Refinement with FlexibleCustom.
        This approach uses a structured iterative loop to progressively improve the solution,
        avoiding unnecessary parallelism while still allowing for refinement based on internal feedback.
        It's simpler than the existing workflow but more robust than a single step.
        """
        # Step 1: Use FlexibleCustom in iterative mode to generate an initial solution
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Review the solution to catch any remaining errors or ambiguities
        final_solution = await self.review(pre_solution=initial_solution)

        return final_solution
# Workflow ID: gsm8k_148_0
# Benchmark: gsm8k
# Data Indices: [223, 784, 19]

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
        This is a diverse and efficient workflow using iterative refinement with a flexible custom operator.
        It leverages the 'iterative' reasoning pattern to progressively improve the solution,
        avoiding unnecessary complexity while ensuring robustness through structured refinement.
        """
        # Step 1: Use FlexibleCustom in iterative mode for systematic step-by-step refinement
        solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Solve the problem by breaking it into clear logical steps and refining each iteration."
        )

        # Step 2: Review the final solution for clarity and correctness
        final_solution = await self.review(pre_solution=solution)

        return final_solution
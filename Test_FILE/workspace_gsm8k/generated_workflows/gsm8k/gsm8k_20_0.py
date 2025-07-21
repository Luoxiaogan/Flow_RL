# Workflow ID: gsm8k_20_0
# Benchmark: gsm8k
# Data Indices: [606, 241]

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
        Efficient and diverse workflow using Reflect + FlexibleCustom (Iterative Pattern).
        This pattern allows for structured reasoning with progressive refinement — logical, efficient, and distinct from a single-step approach.
        """
        # Step 1: Initial solution via iterative flexible custom (3 steps: analyze, solve, verify)
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Begin by identifying the key elements of the problem. Then compute the solution step-by-step. Finally, verify your answer."
        )

        # Step 2: Reflect on the solution to uncover potential blind spots or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a final, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Re-evaluate the problem carefully and provide a clear, accurate solution."
        )

        return final_solution
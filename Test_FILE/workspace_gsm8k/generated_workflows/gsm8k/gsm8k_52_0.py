# Workflow ID: gsm8k_52_0
# Benchmark: gsm8k
# Data Indices: [217, 15]

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
        Diverse and efficient workflow using Reflect + FlexibleCustom (Iterative Pattern).
        This structure mimics human meta-cognition: generate, reflect, then refine iteratively.
        It's simple (only 3 steps), effective, and avoids redundancy.
        """
        # Step 1: Generate an initial solution with structured reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "compute", "verify"],
            max_iterations=1
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a refined solution (single pass)
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity and accuracy."
        )

        return final_solution
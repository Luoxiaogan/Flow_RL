# Workflow ID: gsm8k_56_0
# Benchmark: gsm8k
# Data Indices: [694, 621, 117]

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
        Diverse and efficient workflow using Reflect + FlexibleCustom for meta-cognitive refinement.
        This structure avoids redundancy while enabling deep reasoning through reflection.
        """
        # Step 1: Generate an initial solution with structured step-by-step thinking
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Critically reflect on the solution to identify potential blind spots
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a targeted re-solution — this is more efficient than full re-generation
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, provide a refined solution that addresses these points."
        )

        return final_solution
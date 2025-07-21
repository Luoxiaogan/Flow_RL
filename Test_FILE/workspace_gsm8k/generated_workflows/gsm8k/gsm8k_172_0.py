# Workflow ID: gsm8k_172_0
# Benchmark: gsm8k
# Data Indices: [947, 871]

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
        This pattern combines initial reasoning with structured reflection to guide a focused re-solution.
        """
        # Step 1: Generate an initial solution using a flexible sequential approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, focusing on clear logic and accurate arithmetic.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "compute", "verify"]
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted Custom call for refinement
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again, ensuring all assumptions are valid and calculations are precise."
        )

        return final_solution
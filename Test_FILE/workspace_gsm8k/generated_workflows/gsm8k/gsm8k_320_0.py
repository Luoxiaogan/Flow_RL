# Workflow ID: gsm8k_320_0
# Benchmark: gsm8k
# Data Indices: [668, 287]

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
        This pattern uses meta-cognition to improve reasoning iteratively — a novel structure that avoids redundancy while ensuring robustness.
        """
        # Step 1: Generate an initial solution using a structured iterative approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin with a clear breakdown of the problem.",
            reasoning_pattern="iterative",
            steps=["understand", "analyze", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or omissions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a final, improved solution via Custom
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now provide a refined answer."
        )

        return final_solution
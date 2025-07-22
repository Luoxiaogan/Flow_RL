# Workflow ID: gsm8k_373_0
# Benchmark: gsm8k
# Data Indices: [105, 201]

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
        This avoids a single-step solution by incorporating meta-cognition and structured refinement.
        """
        # Step 1: Generate an initial solution using a flexible iterative approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Break the problem into logical steps and refine iteratively."
        )

        # Step 2: Reflect on the initial solution to identify potential weaknesses
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a final, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                       f"Refine your answer based on this critique. Be precise and step-by-step."
        )

        return final_solution
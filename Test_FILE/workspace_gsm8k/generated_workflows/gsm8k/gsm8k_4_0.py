# Workflow ID: gsm8k_4_0
# Benchmark: gsm8k
# Data Indices: [138, 458]

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
        This structure allows for meta-cognitive refinement without excessive complexity.
        """
        # Step 1: Initial solution using iterative reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying what is being asked and break the problem into clear steps.",
            reasoning_pattern="iterative",
            steps=["understand", "decompose", "compute", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the solution to uncover potential blind spots
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a final, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        f"Provide a revised and more accurate answer."
        )

        return final_solution
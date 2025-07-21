# Workflow ID: gsm8k_35_0
# Benchmark: gsm8k
# Data Indices: [128, 270]

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
        Diverse and efficient workflow using iterative refinement with FlexibleCustom.
        This pattern ensures logical progression from initial idea to polished solution.
        """
        # Step 1: Use FlexibleCustom in iterative mode to generate a structured, step-by-step solution
        solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Break the problem into clear steps: identify knowns, plan calculation, execute, then check for consistency."
        )

        # Step 2: Reflect on the solution to catch potential errors or assumptions
        reflection = await self.reflect(solution)

        # Step 3: Use reflection to guide a final, improved custom response
        final_solution = await self.custom(
            instruction=f"Based on the following reflection:\n{reflection}\n\nProvide a refined, accurate answer. Be concise but thorough."
        )

        return final_solution
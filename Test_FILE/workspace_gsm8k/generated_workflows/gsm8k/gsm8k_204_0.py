# Workflow ID: gsm8k_204_0
# Benchmark: gsm8k
# Data Indices: [665, 309]

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
        Diverse and efficient workflow using iterative refinement with flexible custom reasoning.
        This pattern uses a structured, step-by-step approach (sequential) to solve the problem,
        then applies one round of review to improve clarity and correctness — balancing simplicity
        with effectiveness.
        """
        # Step 1: Use FlexibleCustom in sequential mode for structured reasoning
        solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break the problem into clear logical steps and verify each."
        )

        # Step 2: Review the solution once to polish reasoning and fix any errors
        final_solution = await self.review(pre_solution=solution)

        return final_solution
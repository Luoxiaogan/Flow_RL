# Workflow ID: gsm8k_124_1
# Benchmark: gsm8k
# Data Indices: [22, 893]

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
        Diverse workflow using Reflect and Regenerate pattern: 
        Generate an initial solution, reflect on its weaknesses, then use that reflection to guide a targeted revision.
        This approach mimics human metacognition — identify flaws before improving — and is efficient with only two steps.
        """
        # Step 1: Generate an initial solution using a structured Custom call
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution to uncover potential issues or blind spots
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection, revise the solution: {reflection}. Provide a clear, accurate answer."
        )

        return final_solution
# Workflow ID: gsm8k_339_0
# Benchmark: gsm8k
# Data Indices: [763, 484, 956]

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
        This is a diverse and efficient workflow using Reflect + Custom for meta-cognitive refinement.
        It's simple (only 3 steps), but uses reflection to guide improvement — a novel structure
        that avoids redundant computation while enhancing solution quality.
        """
        # Step 1: Generate initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Explain each step clearly."
        )

        # Step 2: Critically reflect on the solution to identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution — no unnecessary iterations
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution based on this insight."
        )

        return final_solution
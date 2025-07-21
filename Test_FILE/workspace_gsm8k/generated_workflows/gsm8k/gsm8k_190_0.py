# Workflow ID: gsm8k_190_0
# Benchmark: gsm8k
# Data Indices: [990, 511, 499]

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
        Diverse and efficient workflow using Reflect + Custom for meta-cognitive improvement.
        This pattern encourages critical thinking about the solution before generating a final answer.
        It's simple (only 3 steps), logical, and avoids unnecessary complexity while being effective.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into clear, logical steps. Explain each step thoroughly."
        )

        # Step 2: Critically reflect on the solution to identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a revised, more accurate solution that addresses the identified issues."
        )

        return final_solution
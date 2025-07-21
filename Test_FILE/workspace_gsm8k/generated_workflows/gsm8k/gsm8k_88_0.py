# Workflow ID: gsm8k_88_0
# Benchmark: gsm8k
# Data Indices: [522, 208]

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
        Diverse and efficient workflow using iterative refinement with a flexible custom operator.
        This pattern combines structured reasoning (via FlexibleCustom) with reflection for meta-cognitive improvement.
        """
        # Step 1: Use FlexibleCustom in iterative mode to generate an initial solution through structured steps
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["understand_problem", "formulate_equation", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Solve the problem by breaking it into logical steps: understand, formulate, solve, verify."
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a final improved solution based on the reflection
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        "Now, provide a clear, accurate, and well-structured final answer."
        )

        return final_solution
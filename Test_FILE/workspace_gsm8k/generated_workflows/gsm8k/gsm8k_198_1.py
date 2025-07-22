# Workflow ID: gsm8k_198_1
# Benchmark: gsm8k
# Data Indices: [91, 833, 260]

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
        This is a diverse and iterative workflow using the 'Iterative Refinement' pattern.
        It starts with a simple initial solution, then applies the Review operator twice
        to progressively refine the answer. Each review step improves clarity, logic, or accuracy.
        This mimics how humans improve solutions through multiple passes of critical thinking.
        """
        # Step 1: Generate a basic solution using a flexible custom operator in sequential mode
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear steps and showing all calculations.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "solve", "verify"]
        )

        # Step 2: First refinement — review the initial solution for logical gaps or unclear explanations
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — apply another round of review to polish structure, fix subtle errors, and enhance clarity
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
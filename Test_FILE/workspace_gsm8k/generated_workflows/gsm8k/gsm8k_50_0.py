# Workflow ID: gsm8k_50_0
# Benchmark: gsm8k
# Data Indices: [659, 912]

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
        Diverse and efficient workflow using iterative refinement with reflection.
        This pattern combines meta-cognition (reflection) with targeted improvement (review),
        avoiding unnecessary complexity while enhancing accuracy through structured feedback loops.
        """
        # Step 1: Generate an initial solution using a flexible custom operator in sequential mode
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear steps: identify knowns, unknowns, apply relevant formulas, and compute the final result.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_formulas", "compute_final"]
        )

        # Step 2: Reflect on the solution to uncover potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a focused review that improves the solution
        final_solution = await self.review(pre_solution=initial_solution)

        return final_solution
# Workflow ID: gsm8k_261_1
# Benchmark: gsm8k
# Data Indices: [959, 374, 371]

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
        This is a diverse and efficient workflow using the Iterative Refinement + Reflect-and-Regenerate hybrid pattern.
        It starts with an initial solution, then uses iterative refinement (Review) to improve it step-by-step,
        while also incorporating a critical reflection at each stage to guide improvements — not just fix errors but rethink strategy.
        This creates a meta-cognitive loop that enhances both accuracy and reasoning depth.
        """

        # Step 1: Generate an initial solution with clear step-by-step breakdown
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller steps. Show all calculations explicitly."
        )

        # Step 2: Use iterative refinement — apply Review multiple times to progressively improve the solution
        refined_solution = initial_solution
        for i in range(2):  # Two rounds of refinement
            # Step 3: Critically reflect on current solution to uncover assumptions or blind spots
            reflection = await self.reflect(pre_solution=refined_solution)

            # Step 4: Use reflection to guide a targeted revision (not just general editing)
            refined_solution = await self.review(
                pre_solution=refined_solution,
                instruction=f"Based on this reflection: '{reflection}'. Now, revise your solution focusing on clarity, logical flow, and correctness. Do not introduce new assumptions unless justified."
            )

        return refined_solution
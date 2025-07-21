# Workflow ID: gsm8k_167_1
# Benchmark: gsm8k
# Data Indices: [765, 337, 986]

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
        This is a diverse and robust workflow using the Iterative Refinement pattern.
        It starts with an initial solution, then applies two rounds of review to progressively improve clarity, correctness, and completeness.
        This mimics how humans refine their thinking — first draft, then critique, then polish — ensuring high-quality output without overfitting to any single strategy.
        """

        # --- Step 1: Generate an initial solution using a clear, step-by-step instruction ---
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into small, logical steps. Show all intermediate calculations explicitly."
        )

        # --- Step 2: First Review — Improve clarity, fix obvious errors, and ensure logical flow ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second Review — Further enhance precision, eliminate ambiguity, and verify internal consistency ---
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
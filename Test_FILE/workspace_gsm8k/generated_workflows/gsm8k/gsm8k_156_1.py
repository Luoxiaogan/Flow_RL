# Workflow ID: gsm8k_156_1
# Benchmark: gsm8k
# Data Indices: [935, 614, 155]

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
        This is a diverse workflow using the Iterative Refinement pattern with structured review loops.
        1. Generate an initial solution.
        2. Apply Review twice to progressively refine it — each time improving clarity, accuracy, and completeness.
        3. Final output is the result of two rounds of critical feedback and improvement.
        """
        # --- Step 1: Generate initial solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into clear logical steps. Be precise."
        )

        # --- Step 2: First refinement via Review ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second refinement via Review (iterative improvement) ---
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
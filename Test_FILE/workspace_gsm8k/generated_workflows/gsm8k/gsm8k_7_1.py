# Workflow ID: gsm8k_7_1
# Benchmark: gsm8k
# Data Indices: [917, 698]

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
        This is a diverse workflow using the Iterative Refinement pattern.
        1. Generate an initial solution with a general-purpose custom call.
        2. Apply Review operator twice to progressively refine the solution — each review improves clarity, logic, and completeness.
        3. The final result is a well-refined answer through structured iterative improvement.
        """
        # --- Step 1: Generate initial solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly and logically."
        )

        # --- Step 2: First refinement via Review ---
        first_refinement = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second refinement via Review (progressive improvement) ---
        second_refinement = await self.review(pre_solution=first_refinement)

        return second_refinement
# Workflow ID: gsm8k_141_1
# Benchmark: gsm8k
# Data Indices: [883, 2]

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
        Iterative Refinement Workflow using Review Operator Twice.
        Step 1: Generate an initial solution using a structured reasoning approach.
        Step 2: Apply the Review operator twice to progressively refine the solution.
        This mimics human-like iterative improvement — first draft → feedback → refinement → final polish.
        """

        # --- STEP 1: Initial Solution via FlexibleCustom (Sequential Reasoning) ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by following a clear, step-by-step logical process.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # --- STEP 2: First Review — Improve clarity and correctness ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- STEP 3: Second Review — Address subtle flaws or assumptions missed earlier ---
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined
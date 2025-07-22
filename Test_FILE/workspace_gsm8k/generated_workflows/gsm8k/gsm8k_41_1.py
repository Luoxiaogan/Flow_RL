# Workflow ID: gsm8k_41_1
# Benchmark: gsm8k
# Data Indices: [84, 588, 504]

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
        It starts with an initial solution, then applies Review at least twice to progressively improve it.
        This mimics human-like reasoning where early attempts are refined through critical feedback.
        """
        # --- Step 1: Generate an initial solution using a general-purpose instruction ---
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # --- Step 2: Apply iterative refinement using Review at least twice ---
        current_solution = initial_solution
        for iteration in range(2):  # Two rounds of refinement
            # Use Review to critique and rewrite the current solution
            current_solution = await self.review(pre_solution=current_solution)

        # --- Step 3: Final output (no ensemble or reflection needed here — this is pure iterative improvement) ---
        return current_solution
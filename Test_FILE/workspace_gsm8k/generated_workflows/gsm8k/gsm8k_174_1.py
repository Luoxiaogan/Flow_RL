# Workflow ID: gsm8k_174_1
# Benchmark: gsm8k
# Data Indices: [876, 672]

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
        Iterative Refinement Workflow: Generate an initial solution, then refine it twice using the Review operator.
        This approach focuses on progressive improvement through structured feedback loops rather than parallel exploration or reflection-based regeneration.
        """
        # --- Step 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Clearly identify what is given, what needs to be found, and how to connect them using logical reasoning."
        )

        # --- Step 2: First Iteration of Refinement ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second Iteration of Refinement ---
        second_refined = await self.review(pre_solution=first_refined)

        # --- Optional: Final Check (if needed) ---
        # In this pattern, we stop after two reviews — a minimal but effective refinement loop.
        return second_refined
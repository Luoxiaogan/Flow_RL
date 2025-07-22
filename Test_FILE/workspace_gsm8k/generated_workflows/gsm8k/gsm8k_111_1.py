# Workflow ID: gsm8k_111_1
# Benchmark: gsm8k
# Data Indices: [918, 212]

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
        Efficient and logically distinct workflow using Iterative Refinement with a single initial solution.
        Step 1: Generate an initial solution using Custom.
        Step 2: Use Review to iteratively improve it — one refinement step is sufficient for most problems.
        This avoids unnecessary parallelism or reflection overhead while still enabling improvement.
        """

        # --- STEP 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations clearly. Be precise with units and operations."
        )

        # --- STEP 2: Single Iteration of Refinement ---
        refined_solution = await self.review(pre_solution=initial_solution)

        return refined_solution
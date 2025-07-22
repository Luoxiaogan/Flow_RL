# Workflow ID: gsm8k_48_1
# Benchmark: gsm8k
# Data Indices: [949, 377]

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
        Diverse and efficient workflow using Iterative Refinement with FlexibleCustom.
        Step 1: Use FlexibleCustom in iterative mode to generate a progressively refined solution.
        Step 2: Return the final refined result after one round of iteration (max_iterations=1).
        This avoids unnecessary parallelism or reflection overhead while still enabling structured improvement.
        """

        # --- ITERATIVE REFINEMENT USING FLEXIBLECUSTOM ---
        # Configure for iterative refinement: start with an initial approach, then refine
        refined_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by first estimating the answer, then checking consistency with given operations.",
            reasoning_pattern="iterative",
            steps=["estimate", "verify", "adjust"],
            max_iterations=1
        )

        return refined_solution
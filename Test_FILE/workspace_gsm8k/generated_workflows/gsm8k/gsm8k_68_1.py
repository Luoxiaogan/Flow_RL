# Workflow ID: gsm8k_68_1
# Benchmark: gsm8k
# Data Indices: [645, 501]

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
        Iterative Refinement Workflow: Generate an initial solution, then improve it through two rounds of Review.
        This pattern focuses on progressive enhancement rather than ensemble or reflection-based regeneration.
        """
        # --- Step 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break down each part clearly and calculate the total."
        )

        # --- Step 2: First Review (Improve clarity and correctness) ---
        first_revision = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second Review (Refine logic, check assumptions, ensure completeness) ---
        second_revision = await self.review(pre_solution=first_revision)

        # --- Step 4: Return Final Refined Solution ---
        return second_revision
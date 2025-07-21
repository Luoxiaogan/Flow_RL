# Workflow ID: gsm8k_32_1
# Benchmark: gsm8k
# Data Indices: [632, 730, 164]

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
        Iterative Refinement Workflow: Start with a simple solution, then refine it twice using Review.
        This pattern focuses on progressive improvement through targeted critique — no ensembling or reflection-based branching.
        """
        # --- Step 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear and concise."
        )

        # --- Step 2: First Iteration of Refinement ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second Iteration of Refinement ---
        second_refined = await self.review(pre_solution=first_refined)

        # --- Final Output: Return the most refined version ---
        return second_refined
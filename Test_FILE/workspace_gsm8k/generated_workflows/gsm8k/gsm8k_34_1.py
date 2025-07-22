# Workflow ID: gsm8k_34_1
# Benchmark: gsm8k
# Data Indices: [628, 290, 160]

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
        This workflow uses an Iterative Refinement pattern with a single initial solution.
        1. Generate an initial solution using a structured FlexibleCustom call (sequential reasoning).
        2. Use Review to improve it iteratively up to 2 times — this is efficient and avoids parallel overhead.
        3. Return the final refined solution.

        Why this is different:
        - No parallel ensemble or reflection-based regeneration.
        - Uses iterative refinement (like the pattern) but only on one path — simple yet effective.
        - Leverages FlexibleCustom for structured step-by-step reasoning without needing multiple solutions.
        """

        # Step 1: Generate a structured initial solution via FlexibleCustom
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically.",
            reasoning_pattern="sequential",
            steps=["understand", "break_down", "solve_step_by_step", "verify"]
        )

        # Step 2: Refine iteratively — maximum of 2 passes
        current_solution = initial_solution
        for _ in range(2):
            revised = await self.review(pre_solution=current_solution)
            if revised == current_solution:  # If no change, stop early
                break
            current_solution = revised

        return current_solution
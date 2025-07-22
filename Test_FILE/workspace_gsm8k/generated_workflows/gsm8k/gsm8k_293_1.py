# Workflow ID: gsm8k_293_1
# Benchmark: gsm8k
# Data Indices: [49, 929]

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
        This is a diverse workflow using Iterative Refinement with FlexibleCustom.
        Step 1: Use an iterative FlexibleCustom to generate a solution in multiple passes.
        Step 2: After the final iteration, review the result to ensure clarity and correctness.
        This avoids ensemble overhead while still allowing progressive improvement — efficient and logically distinct from the existing workflow.
        """

        # --- ITERATIVE REFINEMENT USING FLEXIBLECUSTOM ---
        iterative_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by iteratively refining your approach.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2  # Two iterations for refinement without overcomplicating
        )

        # --- FINAL REVIEW FOR CLARITY AND CORRECTNESS ---
        final_answer = await self.review(pre_solution=iterative_solution)

        return final_answer
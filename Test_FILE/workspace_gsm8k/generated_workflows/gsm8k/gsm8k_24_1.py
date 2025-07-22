# Workflow ID: gsm8k_24_1
# Benchmark: gsm8k
# Data Indices: [963, 461, 247]

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
        Efficient and diverse workflow using Iterative Refinement with FlexibleCustom.
        1. Use FlexibleCustom in iterative mode to generate an initial solution, then refine it through two iterations.
        2. This avoids ensemble overhead while still improving quality via structured refinement — a more efficient alternative to parallel solutions.
        3. The iterative pattern ensures each step builds on the previous, minimizing redundant work and maximizing logical progression.
        """
        # --- STEP 1: Iterative Refinement Using FlexibleCustom ---
        refined_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Solve this math problem by first analyzing what's given, then solving step-by-step, and finally verifying your answer."
        )

        # --- STEP 2: Final Review for Polish ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer
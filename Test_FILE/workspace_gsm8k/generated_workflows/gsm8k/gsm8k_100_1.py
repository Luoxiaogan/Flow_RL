# Workflow ID: gsm8k_100_1
# Benchmark: gsm8k
# Data Indices: [354, 866]

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
        1. Use a single flexible custom call with iterative pattern to solve the problem in multiple passes.
        2. Each iteration refines the solution based on internal feedback (no external reflection).
        3. This avoids unnecessary branching or parallelism while still enabling progressive improvement.
        """
        # --- Step 1: Iterative Refinement via FlexibleCustom ---
        final_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with iterative refinement.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return final_solution
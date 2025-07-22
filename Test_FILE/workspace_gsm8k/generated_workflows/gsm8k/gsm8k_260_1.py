# Workflow ID: gsm8k_260_1
# Benchmark: gsm8k
# Data Indices: [951, 838]

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
        Efficient workflow using Iterative Refinement with FlexibleCustom.
        1. Use a single, structured iterative flexible custom call to solve the problem step-by-step.
        2. The reasoning pattern is 'iterative' with max_iterations=2, allowing one refinement pass.
        3. This avoids unnecessary parallelism or reflection loops while still enabling improvement.
        4. Simpler than the existing workflow: no ensembling, no reflection-to-custom redirection.
        5. Focuses on internal refinement via structured steps instead of external feedback.
        """

        # Step: Use iterative FlexibleCustom for efficient, self-contained refinement
        solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically by breaking it into steps.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "solve", "verify"],
            max_iterations=2
        )

        return solution
# Workflow ID: gsm8k_279_1
# Benchmark: gsm8k
# Data Indices: [815, 261, 559]

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
        This is a diverse and efficient workflow using:
        - Iterative Refinement via FlexibleCustom (sequential reasoning pattern)
        - No parallelism or ensemble — focused on deep, structured iteration
        - Single reflection step to guide refinement instead of multiple passes
        - Minimal operators: only 3 steps total (flexible_custom → reflect → review)
        
        This design prioritizes efficiency and logical depth over redundancy.
        """

        # Step 1: Use FlexibleCustom with sequential reasoning for structured, step-by-step solving
        solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear, logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Reflect on the solution to identify potential flaws or missing logic
        reflection = await self.reflect(pre_solution=solution)

        # Step 3: Final polish using Review — only if reflection indicates need for improvement
        if "error" in reflection.lower() or "incomplete" in reflection.lower():
            final_answer = await self.review(pre_solution=solution)
        else:
            final_answer = solution

        return final_answer
# Workflow ID: gsm8k_129_1
# Benchmark: gsm8k
# Data Indices: [488, 708]

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
        1. Use iterative reasoning pattern to generate a solution through multiple refinement passes.
        2. This mimics how humans improve their answers by revisiting steps — simple yet effective.
        """
        # --- Step 1: Iterative Refinement via FlexibleCustom ---
        solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "compute", "verify"],
            max_iterations=2
        )

        # --- Step 2: Light Review for Final Polish ---
        final_answer = await self.review(pre_solution=solution)

        return final_answer
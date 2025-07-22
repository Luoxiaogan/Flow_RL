# Workflow ID: gsm8k_243_0
# Benchmark: gsm8k
# Data Indices: [359, 158]

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
        This is a diverse workflow using Iterative Refinement with a structured reasoning pattern.
        Step 1: Generate an initial solution via FlexibleCustom in sequential mode for systematic breakdown.
        Step 2: Apply Review twice to progressively improve the solution — first to fix clarity and logic, then to ensure completeness.
        """
        # Initial solution using structured sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using clear logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "formulate", "solve"]
        )

        # First refinement: Improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Second refinement: Ensure all aspects are addressed and no assumptions are missed
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution
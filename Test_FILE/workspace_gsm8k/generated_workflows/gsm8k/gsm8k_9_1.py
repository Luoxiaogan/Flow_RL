# Workflow ID: gsm8k_9_1
# Benchmark: gsm8k
# Data Indices: [453, 461, 211]

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
        This is a streamlined yet diverse workflow using:
        - A branching strategy via FlexibleCustom with structured steps (analyze → plan → solve → verify)
        - Single-step refinement with Review for efficiency
        - No parallel ensembling or reflection loops — just one clear path with internal structure

        Why it's different:
        - Uses FlexibleCustom in "sequential" mode for systematic reasoning instead of iterative or ensemble methods.
        - Avoids multiple solution generation; focuses on high-quality single-path reasoning.
        - Efficient: Only 3 operators used total (one flexible custom, one review).
        """

        # Step 1: Use FlexibleCustom with sequential reasoning pattern to generate a well-structured solution
        structured_solution = await self.flexible_custom(
            custom_instruction="Follow a logical sequence: first analyze the problem, then plan your approach, solve step-by-step, and finally verify your answer.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            use_structured_output=True
        )

        # Step 2: Apply a single review pass to improve clarity and correctness without over-engineering
        final_answer = await self.review(pre_solution=structured_solution)

        return final_answer
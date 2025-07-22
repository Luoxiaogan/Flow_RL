# Workflow ID: hotpotqa_322_0
# Benchmark: hotpotqa
# Data Indices: [1706, 3202, 155, 1973]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses FlexibleCustom for step-by-step reasoning, Custom for synthesis, 
        and Review for validation to ensure robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = [
            "identify key entities in the question",
            "extract relevant facts from context",
            "trace connections between entities",
            "synthesize intermediate conclusions"
        ]
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps to solve it.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the final answer based on reasoning
        final_answer = await self.custom(instruction="Based on the above reasoning, generate a concise and accurate final answer.")

        # Step 3: Use Review to validate the answer
        validated_answer = await self.review(pre_solution=final_answer)

        # Optional: Ensemble multiple solutions if we had more than one path (e.g., from different flexible_custom runs)
        # But since we're using single-path reasoning here, no ensemble needed.

        return validated_answer
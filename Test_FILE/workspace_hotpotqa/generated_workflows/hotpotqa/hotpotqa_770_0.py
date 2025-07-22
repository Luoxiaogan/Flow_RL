# Workflow ID: hotpotqa_770_0
# Benchmark: hotpotqa
# Data Indices: [2631, 3077, 2704, 3097, 2454]

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
        Uses FlexibleCustom for sequential reasoning to extract and connect facts,
        Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = ["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, focusing on connecting information across different parts of the context.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the detailed reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Review the synthesized answer for accuracy and clarity
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble multiple solutions (if needed) — here we use a simple list with one solution
        ensemble_result = await self.sc_ensemble(solutions=[reviewed_answer])

        return ensemble_result
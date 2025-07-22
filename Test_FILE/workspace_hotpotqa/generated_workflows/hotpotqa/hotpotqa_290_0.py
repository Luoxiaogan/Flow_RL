# Workflow ID: hotpotqa_290_0
# Benchmark: hotpotqa
# Data Indices: [185, 2606, 3193, 1543]

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
        It uses FlexibleCustom for step-by-step fact extraction and connection,
        then Custom for synthesis, followed by Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on structured reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning provided, generate a clear and concise final answer."
        )

        # Step 3: Review the synthesized answer to ensure correctness and clarity
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Optional: Ensemble multiple solutions (e.g., from different reasoning paths) if needed
        # For now, we only have one solution path — but this structure allows expansion
        # ensemble_result = await self.sc_ensemble(solutions=[synthesized_answer, validated_answer])

        return validated_answer
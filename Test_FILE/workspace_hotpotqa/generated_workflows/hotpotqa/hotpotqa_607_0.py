# Workflow ID: hotpotqa_607_0
# Benchmark: hotpotqa
# Data Indices: [1453, 120, 1087, 2796]

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
        It uses flexible custom for step-by-step reasoning, then synthesizes with Custom,
        and finally validates the result using Review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer from the structured reasoning
        synthesized_answer = await self.custom(instruction="Based on the detailed reasoning above, generate the final answer clearly and concisely.")

        # Step 3: Validate the answer using Review
        validated_answer = await self.review(pre_solution=synthesized_answer)

        return validated_answer
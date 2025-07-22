# Workflow ID: hotpotqa_137_0
# Benchmark: hotpotqa
# Data Indices: [3802, 3179, 1045, 378, 3446]

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
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom to synthesize the answer, followed by Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to generate a synthesized answer based on the structured reasoning
        synthesis = await self.custom(instruction="Based on the detailed reasoning above, generate a clear and concise answer.")

        # Step 3: Use Review to validate the synthesized answer
        validated_answer = await self.review(pre_solution=synthesis)

        return validated_answer
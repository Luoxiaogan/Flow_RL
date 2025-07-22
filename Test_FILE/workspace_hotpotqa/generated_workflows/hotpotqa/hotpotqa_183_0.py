# Workflow ID: hotpotqa_183_0
# Benchmark: hotpotqa
# Data Indices: [1096, 823, 1794, 2284, 3752]

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
        Custom for synthesis, and Review for validation to ensure accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # into smaller steps and trace connections across multiple hops
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace the logical connections between facts.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear answer based on the structured reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a concise and accurate answer."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
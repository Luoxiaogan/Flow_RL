# Workflow ID: hotpotqa_430_0
# Benchmark: hotpotqa
# Data Indices: [2678, 3016, 2422, 145]

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
        then Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information across multiple hops
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_related_facts", "connect_information_across_contexts", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on the multi-hop reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Use Review to validate the synthesized answer by checking for consistency
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble with original reasoning if needed (for robustness)
        ensemble_solution = await self.sc_ensemble(solutions=[synthesized_answer, validated_answer])

        return ensemble_solution
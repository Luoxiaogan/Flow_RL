# Workflow ID: hotpotqa_342_0
# Benchmark: hotpotqa
# Data Indices: [3871, 2878, 611, 3827]

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
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses flexible custom for structured step-by-step reasoning, 
        followed by synthesis via Custom, then validation via Review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "find_intermediate_connections", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer from the multi-hop reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a clear and concise answer that directly addresses the question."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
# Workflow ID: hotpotqa_249_0
# Benchmark: hotpotqa
# Data Indices: [1211, 1699, 2956, 2795]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information in the context.
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace how each piece of information connects to the next.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "find_intermediate_connections", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on the structured reasoning path.
        synthesized_answer = await self.custom(
            instruction="Based on the logical chain of reasoning above, generate a clear and concise answer that directly addresses the question."
        )

        # Step 3: Review the synthesized answer to ensure accuracy and completeness.
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
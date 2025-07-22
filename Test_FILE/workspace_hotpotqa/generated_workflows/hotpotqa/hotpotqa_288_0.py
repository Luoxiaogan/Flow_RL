# Workflow ID: hotpotqa_288_0
# Benchmark: hotpotqa
# Data Indices: [2083, 1538, 1308, 2797]

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
        It uses FlexibleCustom with sequential reasoning to extract and connect facts,
        then Custom to synthesize the answer, and Review to validate it.
        """
        # Step 1: Use FlexibleCustom (sequential) to break down the problem into steps
        # and trace connections across multiple pieces of information
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace logical connections between entities or facts.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on the structured reasoning
        synthesis = await self.custom(instruction="Based on the reasoning steps above, write a clear and concise answer that addresses the original question.")

        # Step 3: Use Review to validate and refine the synthesized answer
        final_answer = await self.review(pre_solution=synthesis)

        return final_answer
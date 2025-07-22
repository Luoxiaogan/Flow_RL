# Workflow ID: hotpotqa_222_0
# Benchmark: hotpotqa
# Data Indices: [199, 1265, 3540, 1093]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace the connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on extracted reasoning
        synthesis = await self.custom(
            instruction="Based on the reasoning path above, provide a clear and concise final answer."
        )

        # Step 3: Use Review to validate the synthesized answer
        validated_answer = await self.review(pre_solution=synthesis)

        return validated_answer
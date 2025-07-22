# Workflow ID: hotpotqa_468_0
# Benchmark: hotpotqa
# Data Indices: [599, 854, 1930, 1259, 1002]

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
        # and trace connections between entities or concepts across multiple hops
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and their relationships across multiple steps.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the multi-hop reasoning
        synthesis = await self.custom(
            instruction="Based on the reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Review the synthesized answer to validate accuracy and logic
        final_answer = await self.review(pre_solution=synthesis)

        return final_answer
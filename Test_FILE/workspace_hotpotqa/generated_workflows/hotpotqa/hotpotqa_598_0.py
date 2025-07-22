# Workflow ID: hotpotqa_598_0
# Benchmark: hotpotqa
# Data Indices: [3513, 1477, 16, 3113, 2397]

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
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the solution with a custom operator, and finally validates it via review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and trace multi-hop connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identify key entities, and trace logical connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear, structured answer based on the multi-hop reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the multi-hop reasoning, synthesize a concise and accurate answer. Explain each step clearly."
        )

        # Step 3: Review the synthesized answer to validate correctness and improve clarity
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
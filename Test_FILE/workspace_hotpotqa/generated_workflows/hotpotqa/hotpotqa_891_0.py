# Workflow ID: hotpotqa_891_0
# Benchmark: hotpotqa
# Data Indices: [1157, 1468, 3153, 3844, 2500]

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
        then synthesizes the answer using Custom, and finally validates it with Review.
        """
        # Step 1: Use FlexibleCustom (sequential) to break down the problem into steps
        # and extract relevant facts across multiple hops
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Synthesize the final answer based on the structured reasoning
        synthesis = await self.custom(
            instruction="Based on the extracted facts and connections, synthesize a clear and accurate answer to the question."
        )

        # Step 3: Validate the synthesized answer through review
        validated_answer = await self.review(pre_solution=synthesis)

        return validated_answer
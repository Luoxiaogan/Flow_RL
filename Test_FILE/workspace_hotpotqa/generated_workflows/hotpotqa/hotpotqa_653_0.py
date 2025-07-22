# Workflow ID: hotpotqa_653_0
# Benchmark: hotpotqa
# Data Indices: [940, 3667, 593, 1452, 2141]

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
        # and extract relevant information step by step (e.g., identify entities, find connections).
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer from the multi-hop reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the multi-step reasoning provided, generate a clear and concise final answer."
        )

        # Step 3: Use Review to validate the synthesized answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        return validated_answer
# Workflow ID: hotpotqa_680_0
# Benchmark: hotpotqa
# Data Indices: [3739, 390, 1393, 539, 1821]

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
        then synthesizes the answer with a custom operator, and finally reviews it for accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning
        synthesis = await self.custom(
            instruction="Based on the step-by-step reasoning above, provide a clear and concise final answer."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        validated_answer = await self.review(pre_solution=synthesis)

        return validated_answer
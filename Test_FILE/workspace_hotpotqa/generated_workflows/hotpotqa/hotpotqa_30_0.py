# Workflow ID: hotpotqa_30_0
# Benchmark: hotpotqa
# Data Indices: [3362, 1597, 986, 1123, 529]

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
        It uses FlexibleCustom for step-by-step reasoning, Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the answer based on extracted facts
        solution2 = await self.custom(
            instruction="Based on the reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Use Review to validate the synthesized answer
        final_solution = await self.review(pre_solution=solution2)

        return final_solution
# Workflow ID: hotpotqa_53_0
# Benchmark: hotpotqa
# Data Indices: [1837, 1777, 1086, 3611, 841]

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
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections across multiple pieces of context
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using Custom to synthesize the output from flexible_custom
        synthesized_answer = await self.custom(
            instruction="Based on the structured reasoning above, generate a clear and concise answer."
        )

        # Step 3: Validate and refine the answer using Review
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
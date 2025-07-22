# Workflow ID: hotpotqa_110_0
# Benchmark: hotpotqa
# Data Indices: [704, 3160, 1710, 2643, 2679]

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
        # and trace connections across multiple pieces of information
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and explain how each piece connects to the next.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Synthesize the multi-hop solution using Custom to ensure clarity
        synthesized_solution = await self.custom(
            instruction="Based on the multi-hop reasoning above, provide a clear and concise answer."
        )

        # Step 3: Validate the solution using Review to refine any logical gaps
        final_solution = await self.review(pre_solution=synthesized_solution)

        return final_solution
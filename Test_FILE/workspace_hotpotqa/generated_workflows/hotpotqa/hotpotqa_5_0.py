# Workflow ID: hotpotqa_5_0
# Benchmark: hotpotqa
# Data Indices: [2272, 2533, 2339, 2972, 3131]

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
        # and trace connections across multiple hops
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and connecting information logically.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear, structured answer based on the reasoned solution
        synthesized_answer = await self.custom(
            instruction="Based on the logical chain of reasoning, generate a concise and accurate answer."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
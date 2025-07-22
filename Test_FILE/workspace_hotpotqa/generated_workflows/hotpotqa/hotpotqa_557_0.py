# Workflow ID: hotpotqa_557_0
# Benchmark: hotpotqa
# Data Indices: [1304, 1366, 3529, 2664]

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
        It uses FlexibleCustom for structured multi-hop reasoning, followed by Custom for synthesis and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into smaller steps
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller, logical steps to identify key facts and connections.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the solution based on the structured reasoning
        synthesized_solution = await self.custom(
            instruction="Based on the step-by-step breakdown, generate a clear and concise answer with reasoning."
        )

        # Step 3: Use Review to validate and refine the synthesized solution
        final_solution = await self.review(pre_solution=synthesized_solution)

        return final_solution
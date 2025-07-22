# Workflow ID: hotpotqa_415_0
# Benchmark: hotpotqa
# Data Indices: [3101, 2153, 2970, 1568, 3904]

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
        then synthesizes the answer with a custom operator, and finally validates it via review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and connect information
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of evidence.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on structured reasoning
        synthesis = await self.custom(
            instruction="Based on the step-by-step reasoning, generate a clear and concise answer with justification."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        validated_answer = await self.review(pre_solution=synthesis)

        return validated_answer
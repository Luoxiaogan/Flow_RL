# Workflow ID: hotpotqa_634_0
# Benchmark: hotpotqa
# Data Indices: [1489, 1387, 2800, 3697]

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
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the answer based on extracted information
        solution_2 = await self.custom(
            instruction="Based on the reasoning above, provide a clear and concise final answer."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        final_solution = await self.review(pre_solution=solution_2)

        return final_solution
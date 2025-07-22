# Workflow ID: hotpotqa_452_0
# Benchmark: hotpotqa
# Data Indices: [1368, 2100, 3910, 3426, 1729]

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
        It uses FlexibleCustom for step-by-step fact extraction and connection,
        followed by Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and extract key facts from context in a structured way
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and identify all relevant facts.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the extracted information into a coherent answer
        solution_step2 = await self.custom(
            instruction="Based on the facts you've identified, generate a clear and logical explanation that directly answers the question."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        final_solution = await self.review(pre_solution=solution_step2)

        return final_solution
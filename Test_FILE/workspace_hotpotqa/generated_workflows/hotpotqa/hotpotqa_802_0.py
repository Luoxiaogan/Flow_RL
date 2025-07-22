# Workflow ID: hotpotqa_802_0
# Benchmark: hotpotqa
# Data Indices: [2774, 1029, 1134, 3330, 411]

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
        then Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using Custom to synthesize based on extracted facts
        solution_step2 = await self.custom(
            instruction="Based on the reasoning path above, generate a clear and concise answer with justification."
        )

        # Step 3: Review the generated answer to validate and refine it
        final_solution = await self.review(pre_solution=solution_step2)

        return final_solution
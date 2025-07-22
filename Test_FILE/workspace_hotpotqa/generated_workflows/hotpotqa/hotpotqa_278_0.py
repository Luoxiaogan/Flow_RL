# Workflow ID: hotpotqa_278_0
# Benchmark: hotpotqa
# Data Indices: [954, 540, 1686, 3105]

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
        This is a streamlined workflow for multi-hop question answering using FlexibleCustom
        with structured reasoning steps: extract_entities, find_connections, synthesize_answer.
        The solution is refined via review and ensemble to ensure accuracy.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step by first extracting key entities, then finding connections between them, and finally synthesizing a coherent answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Review the multi-hop solution for potential errors or omissions
        reviewed_solution = await self.review(pre_solution=multi_hop_solution)

        # Step 4: Ensemble the direct answer and the reviewed multi-hop solution
        final_solution = await self.sc_ensemble(solutions=[direct_answer, reviewed_solution])

        return final_solution
# Workflow ID: hotpotqa_545_0
# Benchmark: hotpotqa
# Data Indices: [2839, 2962, 827, 2433, 1902]

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
        It uses flexible custom reasoning to break down the problem into key steps: extract_entities, find_connections, synthesize_answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to decompose and connect information
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step: first identify key entities, then find connections between them, and finally synthesize the answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Review the generated solution for accuracy and clarity
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using the reviewed solution as context
        final_answer = await self.answer_generate()

        return final_answer
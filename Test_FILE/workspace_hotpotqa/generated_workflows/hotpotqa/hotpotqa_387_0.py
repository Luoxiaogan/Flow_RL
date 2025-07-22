# Workflow ID: hotpotqa_387_0
# Benchmark: hotpotqa
# Data Indices: [1039, 2917, 2508, 1507]

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
        This is a streamlined workflow for multi-hop question answering using flexible custom reasoning.
        It breaks down the problem into structured steps: extract entities, find connections, and synthesize answer.
        """
        # Step 1: Use FlexibleCustom to perform structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem by first identifying key entities, then finding relationships between them, and finally synthesizing a clear answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        return solution
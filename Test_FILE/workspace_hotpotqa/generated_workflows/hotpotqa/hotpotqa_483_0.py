# Workflow ID: hotpotqa_483_0
# Benchmark: hotpotqa
# Data Indices: [3724, 1891, 2966, 523]

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
        It uses flexible custom reasoning to break down the problem into steps,
        then synthesizes the answer based on extracted entities and connections.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities and find connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step: first identify key entities, then find relationships between them, and finally synthesize an answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        return solution
# Workflow ID: hotpotqa_518_0
# Benchmark: hotpotqa
# Data Indices: [1903, 3332, 3527, 2936, 2858]

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
        It uses flexible custom reasoning to break down the problem into key steps,
        then synthesizes an answer based on extracted entities and connections.
        """
        # Step 1: Use FlexibleCustom with multi-hop reasoning pattern to extract entities and trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identify key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        return solution
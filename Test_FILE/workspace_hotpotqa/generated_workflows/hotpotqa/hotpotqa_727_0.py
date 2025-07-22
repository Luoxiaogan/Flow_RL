# Workflow ID: hotpotqa_727_0
# Benchmark: hotpotqa
# Data Indices: [1233, 3276, 2877, 2925]

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
        This is a streamlined workflow graph for multi-hop question answering.
        It uses FlexibleCustom with structured reasoning steps to break down the problem,
        then synthesizes the answer based on extracted entities and connections.
        """
        # Step 1: Use flexible custom to extract entities and trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and identify key entities and their relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        return solution
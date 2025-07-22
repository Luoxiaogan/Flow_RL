# Workflow ID: hotpotqa_13_0
# Benchmark: hotpotqa
# Data Indices: [1918, 2337, 637, 636, 1808]

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
        It uses FlexibleCustom with structured reasoning steps to break down complex problems.
        """
        # Step 1: Use FlexibleCustom to extract entities and find connections in the problem
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Synthesize the answer based on the reasoned path
        final_answer = await self.flexible_custom(
            custom_instruction="Synthesize the final answer using the reasoning path from previous step.",
            reasoning_pattern="sequential",
            steps=["synthesize_answer"]
        )

        return final_answer
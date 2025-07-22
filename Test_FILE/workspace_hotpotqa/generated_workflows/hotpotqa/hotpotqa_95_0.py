# Workflow ID: hotpotqa_95_0
# Benchmark: hotpotqa
# Data Indices: [92, 925, 3306, 1447]

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
        It uses FlexibleCustom with structured reasoning steps to efficiently solve complex problems.
        """
        # Step 1: Use FlexibleCustom to extract entities and trace connections in a sequential manner
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate final answer based on the structured reasoning path
        final_answer = await self.answer_generate()

        # Step 3: Optionally review the final answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer
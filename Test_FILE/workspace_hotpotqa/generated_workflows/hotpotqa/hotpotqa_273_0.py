# Workflow ID: hotpotqa_273_0
# Benchmark: hotpotqa
# Data Indices: [453, 3819, 801, 3998, 3003]

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
        """
        # Step 1: Use FlexibleCustom to break down the problem into key steps (sequential reasoning)
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, focusing on identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate final answer using the structured solution from FlexibleCustom
        final_answer = await self.answer_generate()

        return final_answer
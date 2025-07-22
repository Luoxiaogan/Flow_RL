# Workflow ID: hotpotqa_396_0
# Benchmark: hotpotqa
# Data Indices: [3074, 1095, 2032, 1753]

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
        It leverages structured step-by-step reasoning to extract entities, find connections, and synthesize the final answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into key steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem by first extracting key entities, then finding logical connections between them, and finally synthesizing the answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        return solution
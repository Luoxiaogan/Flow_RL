# Workflow ID: hotpotqa_397_0
# Benchmark: hotpotqa
# Data Indices: [2461, 530, 142, 838, 1726]

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
        This is a streamlined workflow for multi-hop question answering using FlexibleCustom for structured reasoning.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key reasoning steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem by identifying key entities, finding connections between them, and synthesizing the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        return solution
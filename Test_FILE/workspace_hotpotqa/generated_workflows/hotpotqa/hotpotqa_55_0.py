# Workflow ID: hotpotqa_55_0
# Benchmark: hotpotqa
# Data Indices: [2738, 526, 1504, 2608]

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
        It uses FlexibleCustom with sequential reasoning to break down complex problems.
        """
        # Step 1: Use flexible custom to extract entities and find connections in a structured way
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step by first extracting key entities, then finding logical connections between them, and finally synthesizing an answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally review the generated solution for accuracy
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer based on the reviewed solution
        final_answer = await self.answer_generate()

        return final_answer
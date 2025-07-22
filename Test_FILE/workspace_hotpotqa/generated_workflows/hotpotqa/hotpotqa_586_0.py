# Workflow ID: hotpotqa_586_0
# Benchmark: hotpotqa
# Data Indices: [3093, 1175, 1113, 1595]

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
        It uses FlexibleCustom with sequential reasoning to break down complex problems step-by-step.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break the problem into smaller steps: extract key entities, find connections between them, and synthesize an answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Review the generated solution for potential errors or omissions
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer based on the reviewed solution
        final_answer = await self.answer_generate()

        return final_answer
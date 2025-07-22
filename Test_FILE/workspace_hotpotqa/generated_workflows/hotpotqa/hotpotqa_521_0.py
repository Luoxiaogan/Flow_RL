# Workflow ID: hotpotqa_521_0
# Benchmark: hotpotqa
# Data Indices: [1241, 2682, 2412, 116]

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
        It uses FlexibleCustom with sequential reasoning to extract entities, find connections, and synthesize the answer.
        """
        # Step 1: Use flexible custom to break down the problem into steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using entity extraction, connection finding, and synthesis.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Review the generated solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate a final answer based on the refined solution
        final_answer = await self.answer_generate()

        return final_answer
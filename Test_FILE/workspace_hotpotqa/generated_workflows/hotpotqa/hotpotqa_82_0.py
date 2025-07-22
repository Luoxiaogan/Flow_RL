# Workflow ID: hotpotqa_82_0
# Benchmark: hotpotqa
# Data Indices: [2630, 2458, 52, 544, 1721]

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
        Uses FlexibleCustom with sequential reasoning steps to break down complex problems.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Review the generated solution for clarity and correctness
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer based on the reviewed solution
        final_answer = await self.answer_generate()

        return final_answer
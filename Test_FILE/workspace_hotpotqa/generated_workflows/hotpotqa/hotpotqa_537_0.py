# Workflow ID: hotpotqa_537_0
# Benchmark: hotpotqa
# Data Indices: [2087, 175, 1219, 1789]

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
        It uses flexible custom reasoning to break down the problem into steps,
        then synthesizes an answer with iterative refinement.
        """
        # Step 1: Use FlexibleCustom to extract entities and find connections in a structured way
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem by identifying key entities and tracing relationships between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Review the generated solution for accuracy and clarity
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using the refined solution as context
        final_answer = await self.answer_generate()

        return final_answer
# Workflow ID: hotpotqa_102_0
# Benchmark: hotpotqa
# Data Indices: [250, 2456, 737, 2297, 161]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        It first breaks down the problem, then uses flexible custom to trace connections step-by-step,
        followed by generating an answer and reviewing it for correctness.
        """
        # Step 1: Break down the problem into smaller steps
        decomposition = await self.custom(instruction="Can you break down the problem into smaller steps?")

        # Step 2: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 3: Generate final answer based on the structured reasoning
        final_answer = await self.answer_generate()

        # Step 4: Review the final answer for accuracy and clarity
        refined_answer = await self.review(pre_solution=final_answer)

        return refined_answer
# Workflow ID: hotpotqa_402_0
# Benchmark: hotpotqa
# Data Indices: [1638, 1230, 3835, 3406]

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
        """
        # Step 1: Use FlexibleCustom to perform step-by-step reasoning across multiple hops
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information logically.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate final answer based on the structured reasoning path
        final_answer = await self.answer_generate()

        # Step 3: Review the final answer to ensure correctness and clarity
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer
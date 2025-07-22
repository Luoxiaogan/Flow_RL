# Workflow ID: hotpotqa_148_0
# Benchmark: hotpotqa
# Data Indices: [2760, 1895, 3280, 3081, 3868]

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
        It first breaks down the problem, then traces connections step-by-step, and finally refines the answer.
        """
        # Step 1: Use flexible custom to perform sequential multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information in a logical sequence.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        final_answer = await self.answer_generate()

        # Step 3: Review the generated answer to improve clarity and correctness
        refined_answer = await self.review(pre_solution=final_answer)

        return refined_answer
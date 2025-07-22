# Workflow ID: hotpotqa_404_0
# Benchmark: hotpotqa
# Data Indices: [2268, 2288, 1486, 2758]

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
        It uses flexible custom for step-by-step reasoning, then reviews the result for accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and connect facts
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and connect each piece of information logically.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_related_facts", "trace_logical_connections", "synthesize_answer"]
        )

        # Step 2: Review the generated solution to improve clarity and correctness
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer based on the reviewed solution
        final_answer = await self.answer_generate()

        return final_answer
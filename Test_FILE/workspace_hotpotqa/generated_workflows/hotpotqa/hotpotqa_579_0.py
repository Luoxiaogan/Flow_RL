# Workflow ID: hotpotqa_579_0
# Benchmark: hotpotqa
# Data Indices: [3638, 1531, 2609, 3209]

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
        This is a workflow graph for multi-hop question answering with iterative refinement.
        Starts with an initial answer, then iteratively reviews and refines it using the context.
        """
        # Step 1: Generate an initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use iterative review to refine the answer based on context
        refined_answer = await self.flexible_custom(
            custom_instruction="Review the previous answer and refine it step by step, ensuring each reasoning step is grounded in the provided context.",
            reasoning_pattern="iterative",
            steps=["review_previous", "verify_facts", "refine_answer"],
            max_iterations=3
        )
        
        return refined_answer
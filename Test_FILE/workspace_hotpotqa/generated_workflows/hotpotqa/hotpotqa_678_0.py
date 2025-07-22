# Workflow ID: hotpotqa_678_0
# Benchmark: hotpotqa
# Data Indices: [1720, 3664, 3474, 2788]

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
        This is a workflow graph for multi-hop question answering using iterative refinement.
        Starts with an initial answer, then iteratively reviews and refines it based on context.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Iterative refinement using Review
        refined_answer = initial_answer
        for i in range(3):  # 3 iterations of refinement
            review_result = await self.review(pre_solution=refined_answer)
            refined_answer = review_result
        
        # Step 3: Final ensemble with flexible custom reasoning to ensure robustness
        final_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace the reasoning path across multiple hops",
            reasoning_pattern="iterative",
            steps=["identify_key_entities", "find connections between facts", "trace reasoning path", "synthesize final answer"],
            max_iterations=2
        )

        return final_solution
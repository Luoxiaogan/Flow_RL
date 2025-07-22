# Workflow ID: hotpotqa_512_0
# Benchmark: hotpotqa
# Data Indices: [2658, 702, 779, 3143, 124]

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
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of refinement
            review_result = await self.review(pre_solution=refined_answer)
            refined_answer = review_result
        
        # Step 3: Use FlexibleCustom for structured multi-hop reasoning to verify and finalize
        final_answer = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps, trace connections across information sources, and synthesize a final answer.",
            reasoning_pattern="iterative",
            steps=["identify_key_facts", "trace_reasoning_path", "verify_consistency", "derive_final_answer"],
            max_iterations=2
        )
        
        return final_answer
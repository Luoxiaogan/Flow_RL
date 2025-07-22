# Workflow ID: hotpotqa_787_0
# Benchmark: hotpotqa
# Data Indices: [35, 1751, 3624, 848]

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
        
        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for _ in range(3):  # 3 iterations of refinement
            review_result = await self.review(pre_solution=refined_answer)
            refined_answer = review_result
        
        # Step 3: Use FlexibleCustom for structured multi-hop reasoning (sequential steps)
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps to trace connections across information sources.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )
        
        # Step 4: Ensemble the refined answer and multi-hop solution for final output
        ensemble_solution = await self.sc_ensemble(solutions=[refined_answer, multi_hop_solution])
        
        return ensemble_solution
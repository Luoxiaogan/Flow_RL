# Workflow ID: hotpotqa_513_0
# Benchmark: hotpotqa
# Data Indices: [1321, 1250, 1421, 2257, 571]

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
        # Step 1: Generate an initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of refinement
            review_result = await self.review(pre_solution=refined_answer)
            refined_answer = review_result
        
        # Step 3: Use FlexibleCustom for structured multi-hop reasoning if needed
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each hop carefully.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )
        
        # Step 4: Ensemble the refined answer and multi-hop reasoning result
        ensemble_result = await self.sc_ensemble(solutions=[refined_answer, multi_hop_reasoning])
        
        return ensemble_result
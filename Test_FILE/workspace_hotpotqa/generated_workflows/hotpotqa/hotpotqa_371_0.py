# Workflow ID: hotpotqa_371_0
# Benchmark: hotpotqa
# Data Indices: [493, 1604, 1760, 2987, 3416]

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
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Iterative refinement using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of review/refinement
            refined_answer = await self.review(pre_solution=refined_answer)
        
        # Step 3: Use FlexibleCustom for structured multi-hop reasoning (sequential pattern)
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and trace connections between facts.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )
        
        # Step 4: Ensemble the original refined answer and the multi-hop reasoning result
        ensemble_result = await self.sc_ensemble(solutions=[refined_answer, multi_hop_reasoning])
        
        return ensemble_result
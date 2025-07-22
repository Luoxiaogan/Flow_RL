# Workflow ID: hotpotqa_686_0
# Benchmark: hotpotqa
# Data Indices: [480, 1324, 39, 3923, 1815]

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
        Starts with an initial answer, then iteratively reviews and refines it using feedback from context.
        """
        # Step 1: Generate an initial answer (first hop)
        initial_answer = await self.answer_generate()
        
        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of review/refinement
            refined_answer = await self.review(pre_solution=refined_answer)
        
        # Step 3: Use FlexibleCustom for structured multi-hop reasoning as final check
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace the reasoning path across multiple hops.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )
        
        # Step 4: Ensemble the refined answer and multi-hop reasoning to produce the best solution
        ensemble_solution = await self.sc_ensemble(solutions=[refined_answer, multi_hop_reasoning])
        
        return ensemble_solution
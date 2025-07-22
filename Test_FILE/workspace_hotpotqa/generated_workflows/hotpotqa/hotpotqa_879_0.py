# Workflow ID: hotpotqa_879_0
# Benchmark: hotpotqa
# Data Indices: [3035, 2259, 1696, 707, 1150]

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
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()
        
        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of review/refinement
            refined_answer = await self.review(pre_solution=refined_answer)
        
        # Step 3: Use FlexibleCustom for structured multi-hop reasoning (sequential pattern)
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and trace connections across information sources",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )
        
        # Step 4: Ensemble the refined answer and multi-hop reasoning result
        solutions = [refined_answer, multi_hop_reasoning]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer
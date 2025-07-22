# Workflow ID: hotpotqa_822_0
# Benchmark: hotpotqa
# Data Indices: [3295, 162, 911, 2938, 767]

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
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()
        
        # Step 2: Use iterative review to refine the answer based on context
        refined_answer = initial_answer
        for i in range(3):  # Iterative refinement loop (3 iterations)
            new_refined = await self.review(pre_solution=refined_answer)
            if new_refined == refined_answer:  # Early stop if no change
                break
            refined_answer = new_refined
        
        # Step 3: Use flexible custom for structured multi-hop reasoning as a backup
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each hop sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )
        
        # Step 4: Ensemble the two solutions to select the best one
        final_solution = await self.sc_ensemble(solutions=[refined_answer, multi_hop_reasoning])
        
        return final_solution
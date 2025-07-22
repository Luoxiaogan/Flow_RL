# Workflow ID: hotpotqa_501_0
# Benchmark: hotpotqa
# Data Indices: [2838, 1704, 581, 3579, 1394]

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
        
        # Step 3: Use FlexibleCustom for structured multi-hop reasoning as a final check
        multi_hop_refinement = await self.flexible_custom(
            custom_instruction="Break down the reasoning into clear steps to verify the solution.",
            reasoning_pattern="sequential",
            steps=["identify_key_facts", "trace_connections", "validate_conclusions", "synthesize_final_answer"]
        )
        
        # Step 4: Ensemble the refined answer and multi-hop result for final output
        solutions = [refined_answer, multi_hop_refinement]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer
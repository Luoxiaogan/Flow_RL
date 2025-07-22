# Workflow ID: hotpotqa_34_0
# Benchmark: hotpotqa
# Data Indices: [2181, 2009, 863, 984]

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
        # Step 1: Generate an initial hypothesis
        initial_answer = await self.answer_generate()
        
        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for i in range(3):  # Perform 3 iterations of refinement
            revised_answer = await self.review(pre_solution=refined_answer)
            refined_answer = revised_answer
        
        # Step 3: Final ensemble to select best solution from multiple reasoning paths
        # Use FlexibleCustom to explore different reasoning steps (sequential) for robustness
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between them",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )
        
        # Ensemble the final refined answer with the multi-hop solution
        solutions = [refined_answer, multi_hop_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer
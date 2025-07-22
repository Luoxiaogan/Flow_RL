# Workflow ID: hotpotqa_263_0
# Benchmark: hotpotqa
# Data Indices: [1290, 1388, 699, 3017, 735]

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
        # Step 1: Generate an initial answer (hypothesis)
        initial_answer = await self.answer_generate()
        
        # Step 2: Use Review to refine the answer iteratively based on context
        refined_answer = await self.review(pre_solution=initial_answer)
        
        # Step 3: Use FlexibleCustom for structured multi-hop reasoning (iterative pattern)
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections across different pieces of information",
            reasoning_pattern="iterative",
            steps=["identify_key_facts", "find_intermediate_connections", "verify_consistency", "derive_final_answer"],
            max_iterations=3
        )
        
        # Step 4: Ensemble the refined answer with the multi-hop reasoning result
        solutions = [refined_answer, multi_hop_reasoning]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer
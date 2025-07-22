# Workflow ID: hotpotqa_621_0
# Benchmark: hotpotqa
# Data Indices: [1422, 2325, 1890, 427]

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
        
        # Step 2: Use Review to refine the answer iteratively
        refined_answer = initial_answer
        for i in range(3):  # Perform 3 iterations of refinement
            refined_answer = await self.review(pre_solution=refined_answer)
        
        # Step 3: Optionally, use FlexibleCustom for structured multi-hop reasoning
        # This step uses a sequential pattern to break down the problem into steps
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )
        
        # Step 4: Ensemble the refined answer and multi-hop reasoning result
        ensemble_result = await self.sc_ensemble(solutions=[refined_answer, multi_hop_reasoning])
        
        return ensemble_result
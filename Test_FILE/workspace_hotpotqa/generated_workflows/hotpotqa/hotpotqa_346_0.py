# Workflow ID: hotpotqa_346_0
# Benchmark: hotpotqa
# Data Indices: [232, 3514, 380, 1814, 3398]

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
        # Step 1: Generate an initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use Review to refine the answer iteratively
        refined_answer = initial_answer
        for _ in range(3):  # Iterative refinement loop (3 iterations)
            refined_answer = await self.review(pre_solution=refined_answer)
        
        # Step 3: Optionally use FlexibleCustom for structured reasoning if needed
        # (e.g., to break down complex reasoning paths)
        structured_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step carefully",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )
        
        # Step 4: Ensemble the refined answer and structured reasoning to improve robustness
        ensemble_result = await self.sc_ensemble(solutions=[refined_answer, structured_reasoning])
        
        return ensemble_result
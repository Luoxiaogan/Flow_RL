# Workflow ID: hotpotqa_504_0
# Benchmark: hotpotqa
# Data Indices: [3769, 3266, 2088, 673, 112]

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
        # Step 1: Generate initial hypothesis
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom in iterative mode to refine the answer
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with the initial answer and verify each claim against the context. Refine step-by-step until no contradictions remain.",
            reasoning_pattern="iterative",
            steps=["verify_claims", "check_context", "refine_answer"],
            max_iterations=3
        )
        
        # Step 3: Final review to ensure quality
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
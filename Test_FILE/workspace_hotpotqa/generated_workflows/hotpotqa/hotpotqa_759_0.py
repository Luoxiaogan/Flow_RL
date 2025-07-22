# Workflow ID: hotpotqa_759_0
# Benchmark: hotpotqa
# Data Indices: [3599, 1804, 3847, 1566, 3538]

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
        
        # Step 2: Use flexible custom with iterative reasoning to refine the answer
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with the initial answer and verify each claim against the context. Refine iteratively until all steps are logically sound.",
            reasoning_pattern="iterative",
            steps=["verify_claims", "identify_gaps", "refine_answer"],
            max_iterations=3
        )
        
        # Step 3: Review the final refined answer for consistency and clarity
        final_review = await self.review(pre_solution=refined_answer)
        
        return final_review
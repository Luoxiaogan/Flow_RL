# Workflow ID: hotpotqa_503_0
# Benchmark: hotpotqa
# Data Indices: [3348, 236, 3084, 3897, 2448]

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
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom with iterative pattern to refine the answer
        refined_answer = await self.flexible_custom(
            custom_instruction="Refine your answer by verifying each step against the context.",
            reasoning_pattern="iterative",
            steps=["verify_facts", "identify_gaps", "reconstruct_answer"],
            max_iterations=3
        )
        
        # Step 3: Final review to ensure accuracy
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
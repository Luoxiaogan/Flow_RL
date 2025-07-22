# Workflow ID: hotpotqa_738_0
# Benchmark: hotpotqa
# Data Indices: [77, 2418, 2430, 3869, 2295]

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
        # Step 1: Generate an initial answer (first hop)
        initial_answer = await self.answer_generate()
        
        # Step 2: Use iterative review to refine the answer based on context
        refined_answer = initial_answer
        for i in range(3):  # Perform 3 iterations of refinement
            review_result = await self.review(pre_solution=refined_answer)
            refined_answer = review_result
        
        return refined_answer
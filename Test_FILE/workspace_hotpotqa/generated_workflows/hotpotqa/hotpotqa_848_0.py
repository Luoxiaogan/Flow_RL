# Workflow ID: hotpotqa_848_0
# Benchmark: hotpotqa
# Data Indices: [2703, 205, 3995, 3368, 2171]

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
        Starts with an initial answer, then iteratively reviews and refines it using feedback from context.
        """
        # Step 1: Generate an initial answer (hypothesis)
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom to perform iterative reasoning — refine the answer based on context
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with the initial answer and iteratively verify each step using the context. If any part of the answer lacks support or contains errors, revise accordingly.",
            reasoning_pattern="iterative",
            steps=["verify_evidence", "check_consistency", "refine_answer"],
            max_iterations=3
        )
        
        return refined_answer
# Workflow ID: hotpotqa_695_0
# Benchmark: hotpotqa
# Data Indices: [418, 2207, 594, 129]

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
        Starts with an initial answer, then iteratively reviews and refines it using the context.
        """
        # Step 1: Generate an initial hypothesis
        initial_answer = await self.answer_generate()
        
        # Step 2: Use iterative review to refine the answer based on context
        refined_answer = await self.flexible_custom(
            custom_instruction="Review the previous solution step by step, verify facts against the context, and refine the answer if necessary.",
            reasoning_pattern="iterative",
            steps=["verify_facts", "identify_gaps", "refine_answer"],
            max_iterations=3
        )
        
        return refined_answer
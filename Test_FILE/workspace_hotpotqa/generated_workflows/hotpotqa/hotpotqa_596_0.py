# Workflow ID: hotpotqa_596_0
# Benchmark: hotpotqa
# Data Indices: [1576, 3059, 597, 1271]

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
        # Step 1: Generate an initial answer (hypothesis)
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom to perform iterative reasoning with review
        # This enables step-by-step verification and refinement of the answer
        refined_answer = await self.flexible_custom(
            custom_instruction="Review the previous solution step by step, verify facts, and refine the answer based on the context.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )
        
        return refined_answer
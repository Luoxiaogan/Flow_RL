# Workflow ID: hotpotqa_78_0
# Benchmark: hotpotqa
# Data Indices: [3616, 1138, 1988, 1396]

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
        
        # Step 2: Use iterative review to refine the answer based on context
        refined_answer = await self.flexible_custom(
            custom_instruction="Review the previous answer step by step, verify each claim against the context, and refine accordingly.",
            reasoning_pattern="iterative",
            steps=["verify_claims", "identify_gaps", "refine_answer"],
            max_iterations=3
        )
        
        # Step 3: Final ensemble with original and refined answers for robustness
        solutions = [initial_answer, refined_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer
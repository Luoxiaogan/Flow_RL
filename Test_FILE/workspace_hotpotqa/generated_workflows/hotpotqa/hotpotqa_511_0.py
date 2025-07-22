# Workflow ID: hotpotqa_511_0
# Benchmark: hotpotqa
# Data Indices: [2114, 2654, 2041, 728]

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
        This is a workflow graph for multi-hop question answering using iterative reasoning.
        Starts with an initial answer, then iteratively refines it through review and custom reasoning.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom to perform iterative refinement
        # Reasoning pattern: iterative, with steps to verify facts and refine
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with the initial answer, then verify each fact step-by-step and refine based on context.",
            reasoning_pattern="iterative",
            steps=["verify_facts", "check_context", "refine_answer"],
            max_iterations=3
        )
        
        # Step 3: Review the refined answer for final quality check
        final_review = await self.review(pre_solution=refined_answer)
        
        return final_review
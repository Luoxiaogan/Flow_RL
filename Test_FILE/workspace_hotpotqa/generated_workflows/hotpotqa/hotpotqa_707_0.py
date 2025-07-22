# Workflow ID: hotpotqa_707_0
# Benchmark: hotpotqa
# Data Indices: [3826, 1534, 2023, 3768, 2219]

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
        Starts with an initial answer, then iteratively reviews and refines it using structured reasoning.
        """
        # Step 1: Generate initial hypothesis
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom to perform iterative reasoning
        # Reasoning pattern: iterative with steps to extract, verify, refine
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with the initial answer, then verify each step of reasoning against the context, and refine until no further improvements can be made.",
            reasoning_pattern="iterative",
            steps=["extract_key_facts", "verify_with_context", "refine_reasoning"],
            max_iterations=3
        )
        
        # Step 3: Final review to ensure correctness
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
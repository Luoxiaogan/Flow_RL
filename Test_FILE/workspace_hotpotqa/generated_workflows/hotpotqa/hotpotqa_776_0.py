# Workflow ID: hotpotqa_776_0
# Benchmark: hotpotqa
# Data Indices: [882, 1450, 3154, 750, 1094]

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
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom to perform iterative reasoning
        # Reasoning pattern: iterative, steps: ["initial_answer", "review_context", "refine_answer"]
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with the initial answer, then review against context and refine step by step",
            reasoning_pattern="iterative",
            steps=["initial_answer", "review_context", "refine_answer"],
            max_iterations=3
        )
        
        # Step 3: Final review to ensure correctness
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
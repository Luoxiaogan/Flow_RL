# Workflow ID: hotpotqa_760_0
# Benchmark: hotpotqa
# Data Indices: [3336, 60, 3695, 3645, 2080]

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
        Starts with an initial answer, then iteratively reviews and refines it using structured reasoning.
        """
        # Step 1: Generate initial hypothesis
        initial_answer = await self.answer_generate()
        
        # Step 2: Use FlexibleCustom in iterative mode to refine the answer through multiple reasoning cycles
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with an initial answer and progressively refine it by verifying each step against the context.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )
        
        # Step 3: Final review to ensure coherence and correctness
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
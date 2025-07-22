# Workflow ID: hotpotqa_410_0
# Benchmark: hotpotqa
# Data Indices: [2099, 3170, 2922, 2661, 452]

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
        Starts with an initial answer, then iteratively reviews and refines it until convergence.
        """
        # Step 1: Generate an initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom with iterative reasoning to refine the answer
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis, then verify each step against the context and refine iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )
        
        # Step 3: Optionally use Review to further polish the final answer
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
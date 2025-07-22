# Workflow ID: hotpotqa_583_0
# Benchmark: hotpotqa
# Data Indices: [458, 3596, 307, 410, 1378]

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
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom to perform iterative refinement
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with the initial answer and iteratively verify facts against context, refining the solution step by step.",
            reasoning_pattern="iterative",
            steps=["verify_facts", "check_consistency", "refine_conclusion"],
            max_iterations=3
        )
        
        # Step 3: Final review to ensure quality and correctness
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
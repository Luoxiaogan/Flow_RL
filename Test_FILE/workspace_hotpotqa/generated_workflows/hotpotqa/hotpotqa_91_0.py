# Workflow ID: hotpotqa_91_0
# Benchmark: hotpotqa
# Data Indices: [3360, 3970, 2685, 623, 1653]

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
        
        # Step 2: Use flexible custom to perform iterative reasoning
        refined_answer = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps, verify each step against context, and refine the answer iteratively.",
            reasoning_pattern="iterative",
            steps=["identify_key_entities", "find_intermediate_connections", "verify_facts", "synthesize_final_answer"],
            max_iterations=3
        )
        
        # Step 3: Final review to ensure correctness
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
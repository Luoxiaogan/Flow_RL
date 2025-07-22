# Workflow ID: hotpotqa_295_0
# Benchmark: hotpotqa
# Data Indices: [3944, 1334, 3254, 1360]

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
        Starts with an initial answer, then iteratively refines it using Review.
        """
        # Step 1: Generate initial hypothesis
        initial_answer = await self.answer_generate()
        
        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of refinement
            refined_answer = await self.review(pre_solution=refined_answer)
        
        # Step 3: Use FlexibleCustom for structured multi-hop reasoning as a final check
        final_answer = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace connections between pieces of evidence.",
            reasoning_pattern="sequential",
            steps=["identify_key_facts", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )
        
        return final_answer
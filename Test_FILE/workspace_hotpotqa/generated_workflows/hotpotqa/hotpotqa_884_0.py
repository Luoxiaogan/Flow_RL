# Workflow ID: hotpotqa_884_0
# Benchmark: hotpotqa
# Data Indices: [1189, 1475, 3246, 3740, 1191]

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
        # Step 1: Generate an initial hypothesis
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible custom to perform iterative reasoning (multi-hop)
        # Reasoning pattern: iterative with steps to extract, connect, verify, refine
        refined_answer = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, verify facts, and refine the answer iteratively.",
            reasoning_pattern="iterative",
            steps=["extract_key_facts", "identify_connections", "verify_consistency", "refine_answer"],
            max_iterations=3
        )
        
        # Step 3: Review the final refined answer to ensure correctness
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
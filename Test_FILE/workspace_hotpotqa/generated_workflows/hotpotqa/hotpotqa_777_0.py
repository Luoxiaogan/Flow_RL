# Workflow ID: hotpotqa_777_0
# Benchmark: hotpotqa
# Data Indices: [1523, 3778, 1433, 635, 950]

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
        Starts with an initial answer, then iteratively reviews and refines it using flexible custom reasoning.
        """
        # Step 1: Generate an initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible_custom to perform iterative reasoning (multi-hop) on the initial answer
        # Reasoning pattern: iterative, with steps to extract facts, connect information, and refine
        refined_answer = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, trace connections across pieces of evidence, and refine your answer based on context.",
            reasoning_pattern="iterative",
            steps=["extract_facts", "identify_connections", "trace_reasoning_path", "synthesize_answer"],
            max_iterations=3
        )
        
        # Step 3: Review the refined answer to ensure correctness
        final_answer = await self.review(pre_solution=refined_answer)
        
        return final_answer
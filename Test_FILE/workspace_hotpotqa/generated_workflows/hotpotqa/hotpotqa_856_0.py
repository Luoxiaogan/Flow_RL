# Workflow ID: hotpotqa_856_0
# Benchmark: hotpotqa
# Data Indices: [3310, 1268, 883, 2945, 389]

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
        Starts with an initial answer, then refines it through iterative review and flexible custom reasoning.
        """
        # Step 1: Generate initial hypothesis
        initial_answer = await self.answer_generate()

        # Step 2: Use iterative refinement to improve the answer
        refined_answer = initial_answer
        for i in range(3):  # Iterative refinement loop (3 iterations)
            reviewed_answer = await self.review(pre_solution=refined_answer)
            # Use FlexibleCustom to apply structured multi-hop reasoning based on context
            refined_answer = await self.flexible_custom(
                custom_instruction="Break down the problem into smaller steps and reason step-by-step.",
                reasoning_pattern="iterative",
                steps=["identify_key_facts", "trace_connections", "verify_consistency", "synthesize_final_answer"],
                max_iterations=1
            )
        
        return refined_answer
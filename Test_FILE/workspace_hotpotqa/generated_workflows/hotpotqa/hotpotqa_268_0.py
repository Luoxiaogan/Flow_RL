# Workflow ID: hotpotqa_268_0
# Benchmark: hotpotqa
# Data Indices: [3211, 3717, 3445, 3862]

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
        # Step 1: Generate an initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of review/refinement
            refined_answer = await self.review(pre_solution=refined_answer)

        # Step 3: Use FlexibleCustom for structured multi-hop reasoning if needed
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps to trace connections across multiple pieces of information.",
            reasoning_pattern="iterative",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"],
            max_iterations=2
        )

        # Step 4: Ensemble the refined answer and multi-hop reasoning result
        ensemble_result = await self.sc_ensemble(solutions=[refined_answer, multi_hop_reasoning])

        return ensemble_result
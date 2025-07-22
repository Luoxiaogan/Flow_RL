# Workflow ID: hotpotqa_476_0
# Benchmark: hotpotqa
# Data Indices: [2059, 3899, 190, 3777]

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
        It starts with an initial answer, then iteratively reviews and refines it using the context.
        """
        # Step 1: Generate an initial answer (direct reasoning)
        initial_answer = await self.answer_generate()

        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of review/refinement
            new_refined = await self.review(pre_solution=refined_answer)
            if new_refined == refined_answer:
                break  # Stop if no change occurs
            refined_answer = new_refined

        # Step 3: Use FlexibleCustom for structured multi-hop reasoning (sequential pattern)
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 4: Ensemble the initial refined answer and the multi-hop solution
        ensemble_result = await self.sc_ensemble(solutions=[refined_answer, multi_hop_solution])

        return ensemble_result
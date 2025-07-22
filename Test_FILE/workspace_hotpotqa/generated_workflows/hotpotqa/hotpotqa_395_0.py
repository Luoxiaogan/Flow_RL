# Workflow ID: hotpotqa_395_0
# Benchmark: hotpotqa
# Data Indices: [1498, 777, 327, 222, 3185]

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

        # Step 2: Iteratively refine the answer using Review to check and improve
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of refinement
            review_result = await self.review(pre_solution=refined_answer)
            refined_answer = review_result

        # Step 3: Use FlexibleCustom for structured multi-hop reasoning (sequential pattern)
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key facts and connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 4: Ensemble the initial refined answer and the multi-hop solution
        solutions = [refined_answer, multi_hop_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
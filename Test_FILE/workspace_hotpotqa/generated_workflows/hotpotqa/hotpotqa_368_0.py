# Workflow ID: hotpotqa_368_0
# Benchmark: hotpotqa
# Data Indices: [1530, 3881, 1466, 1082, 1855]

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
        Starts with an initial answer, then iteratively reviews and refines it using context.
        """
        # Step 1: Generate an initial hypothesis
        initial_answer = await self.answer_generate()

        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of refinement
            refined_answer = await self.review(pre_solution=refined_answer)

        # Step 3: Use FlexibleCustom to perform structured multi-hop reasoning if needed
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps, trace connections between facts, and synthesize a final answer.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 4: Ensemble the refined answer and multi-hop reasoning output
        solutions = [refined_answer, multi_hop_reasoning]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
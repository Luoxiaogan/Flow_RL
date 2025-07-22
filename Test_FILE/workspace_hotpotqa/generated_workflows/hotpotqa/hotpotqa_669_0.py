# Workflow ID: hotpotqa_669_0
# Benchmark: hotpotqa
# Data Indices: [3452, 449, 989, 3767, 1041]

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
        """
        # Step 1: Generate an initial answer (hypothesis)
        initial_answer = await self.answer_generate()

        # Step 2: Use Review to refine the answer iteratively
        refined_answer = initial_answer
        for _ in range(3):  # Iterative refinement loop (3 iterations max)
            refined_answer = await self.review(pre_solution=refined_answer)

        # Step 3: Use FlexibleCustom with iterative reasoning pattern for deeper multi-hop reasoning
        multi_hop_answer = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections across information sources",
            reasoning_pattern="iterative",
            steps=["identify_key_entities", "find_intermediate_connections", "verify_facts", "synthesize_final_answer"],
            max_iterations=2
        )

        # Step 4: Ensemble the refined answer and multi-hop answer to select best solution
        solutions = [refined_answer, multi_hop_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
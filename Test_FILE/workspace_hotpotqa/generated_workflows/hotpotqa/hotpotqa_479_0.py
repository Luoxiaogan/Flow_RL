# Workflow ID: hotpotqa_479_0
# Benchmark: hotpotqa
# Data Indices: [151, 1728, 2856, 1978, 2894]

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

        # Step 2: Use Review iteratively to refine the answer based on context
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of review/refinement
            refined_answer = await self.review(pre_solution=refined_answer)

        # Step 3: Optionally use FlexibleCustom for structured multi-hop reasoning
        # This step explores multiple reasoning paths and synthesizes the best path
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="iterative",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"],
            max_iterations=2
        )

        # Step 4: Ensemble the final solutions to improve robustness
        solutions = [refined_answer, multi_hop_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
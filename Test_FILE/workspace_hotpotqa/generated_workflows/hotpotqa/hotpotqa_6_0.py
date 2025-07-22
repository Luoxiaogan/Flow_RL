# Workflow ID: hotpotqa_6_0
# Benchmark: hotpotqa
# Data Indices: [2900, 1168, 909, 3216, 1937]

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
        Starts with an initial answer, then iteratively reviews and refines it using the context.
        """
        # Step 1: Generate initial answer (direct reasoning)
        initial_answer = await self.answer_generate()

        # Step 2: Iterative refinement using Review
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of review/refinement
            refined_answer = await self.review(pre_solution=refined_answer)

        # Step 3: Use FlexibleCustom for structured multi-hop reasoning as fallback
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between facts to derive the answer.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 4: Ensemble the two solutions (initial refined + multi-hop) to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[refined_answer, multi_hop_reasoning])

        return ensemble_solution
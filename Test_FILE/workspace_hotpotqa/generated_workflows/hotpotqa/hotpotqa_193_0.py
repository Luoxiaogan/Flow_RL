# Workflow ID: hotpotqa_193_0
# Benchmark: hotpotqa
# Data Indices: [3716, 22, 895, 3347]

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

        # Step 2: Use Review to iteratively refine the answer based on context
        refined_answer = initial_answer
        for _ in range(3):  # Iterative refinement loop (adjustable)
            new_refinement = await self.review(pre_solution=refined_answer)
            if new_refinement == refined_answer:  # No improvement
                break
            refined_answer = new_refinement

        # Step 3: Optionally use FlexibleCustom for structured multi-hop reasoning
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and trace connections between facts.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 4: Ensemble the refined answer and multi-hop solution
        ensemble_result = await self.sc_ensemble(solutions=[refined_answer, multi_hop_solution])

        return ensemble_result
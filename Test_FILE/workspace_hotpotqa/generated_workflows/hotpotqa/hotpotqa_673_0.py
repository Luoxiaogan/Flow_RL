# Workflow ID: hotpotqa_673_0
# Benchmark: hotpotqa
# Data Indices: [3828, 2170, 369, 2195, 428]

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
        Starts with an initial answer, then iteratively reviews and refines it using structured reasoning.
        """
        # Step 1: Generate an initial answer (direct response)
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom to perform iterative refinement based on the context
        refined_answer = await self.flexible_custom(
            custom_instruction="Refine the answer by checking each step of reasoning against the provided context. If any step lacks evidence, revise it.",
            reasoning_pattern="iterative",
            steps=["verify_facts", "check_connections", "refine_reasoning", "synthesize_answer"],
            max_iterations=3
        )

        # Step 3: Review the refined answer to ensure logical consistency and completeness
        final_reviewed_answer = await self.review(pre_solution=refined_answer)

        return final_reviewed_answer
# Workflow ID: hotpotqa_685_0
# Benchmark: hotpotqa
# Data Indices: [1857, 3188, 3317, 2778, 615]

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
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom to perform iterative refinement
        refined_answer = await self.flexible_custom(
            custom_instruction="Refine the answer by verifying facts step-by-step against the context.",
            reasoning_pattern="iterative",
            steps=["verify_facts", "identify_gaps", "reconstruct_answer"],
            max_iterations=3
        )

        # Step 3: Review the refined answer for consistency and correctness
        final_answer = await self.review(pre_solution=refined_answer)

        return final_answer
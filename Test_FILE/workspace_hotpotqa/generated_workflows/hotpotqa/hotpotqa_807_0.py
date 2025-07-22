# Workflow ID: hotpotqa_807_0
# Benchmark: hotpotqa
# Data Indices: [1500, 392, 3244, 239]

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
        # Step 1: Generate an initial answer (hypothesis)
        initial_answer = await self.answer_generate()

        # Step 2: Use iterative refinement via FlexibleCustom to trace multi-hop reasoning
        refined_answer = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and verify each step against the context.",
            reasoning_pattern="iterative",
            steps=["identify_key_entities", "trace_information_path", "verify_evidence", "synthesize_final_answer"],
            max_iterations=3
        )

        # Step 3: Review the refined answer for accuracy and clarity
        final_review = await self.review(pre_solution=refined_answer)

        # Step 4: Ensemble with initial answer to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[initial_answer, final_review])

        return ensemble_solution
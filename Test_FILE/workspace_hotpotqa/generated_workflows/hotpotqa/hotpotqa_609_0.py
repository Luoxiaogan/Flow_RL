# Workflow ID: hotpotqa_609_0
# Benchmark: hotpotqa
# Data Indices: [2816, 357, 3319, 2167, 749]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        It breaks down the problem step-by-step to trace connections across context sources.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and connect information
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between different pieces of context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning from FlexibleCustom
        final_answer = await self.answer_generate()

        # Step 3: Review the generated answer to refine if necessary
        refined_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble with multiple solutions (e.g., from Custom and AnswerGenerate) for robustness
        solutions = [
            solution,
            final_answer,
            refined_answer
        ]
        ensemble_result = await self.sc_ensemble(solutions=solutions)

        return ensemble_result
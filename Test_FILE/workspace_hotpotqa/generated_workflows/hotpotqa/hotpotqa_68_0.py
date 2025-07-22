# Workflow ID: hotpotqa_68_0
# Benchmark: hotpotqa
# Data Indices: [2781, 3340, 2228, 3201]

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
        It breaks down the problem step-by-step and ensures robustness through review and ensemble.
        """
        # Step 1: Use FlexibleCustom for structured sequential multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps. Connect information across different parts of the context to solve it step by step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate a direct answer as a baseline (for comparison or ensemble)
        baseline_answer = await self.answer_generate()

        # Step 3: Review the flexible custom solution to refine any gaps
        refined_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the baseline and refined answers to improve accuracy
        final_answer = await self.sc_ensemble(solutions=[baseline_answer, refined_solution])

        return final_answer
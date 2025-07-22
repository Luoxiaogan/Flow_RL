# Workflow ID: hotpotqa_804_0
# Benchmark: hotpotqa
# Data Indices: [3629, 1484, 455, 829, 2952]

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
        """
        # Step 1: Use FlexibleCustom to perform step-by-step multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each connection sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer directly as a baseline (for ensemble)
        direct_answer = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the direct answer and refined solution to improve robustness
        final_solution = await self.sc_ensemble(solutions=[direct_answer, refined_solution])

        return final_solution
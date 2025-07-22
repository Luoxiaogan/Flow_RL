# Workflow ID: hotpotqa_547_0
# Benchmark: hotpotqa
# Data Indices: [2545, 401, 2907, 1143]

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
        It breaks down the problem step-by-step and integrates review and ensemble for robustness.
        """
        # Step 1: Use FlexibleCustom for sequential multi-hop reasoning
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        answer_from_reasoning = await self.answer_generate()

        # Step 3: Review the generated answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=answer_from_reasoning)

        # Step 4: Generate a direct answer as a baseline for ensemble
        direct_answer = await self.answer_generate()

        # Step 5: Ensemble the reviewed and direct answers for final output
        final_solution = await self.sc_ensemble(solutions=[reviewed_answer, direct_answer])

        return final_solution
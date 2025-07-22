# Workflow ID: hotpotqa_864_0
# Benchmark: hotpotqa
# Data Indices: [1185, 292, 2944, 1782, 1114]

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
        It first generates an initial answer, then refines it through review, and finally uses flexible custom
        to trace multi-hop connections step-by-step for robust reasoning.
        """
        # Step 1: Generate an initial answer directly
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use FlexibleCustom with sequential reasoning pattern to trace multi-hop connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 4: Ensemble the reviewed answer and the multi-hop solution for final accuracy
        solutions = [reviewed_answer, multi_hop_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
# Workflow ID: hotpotqa_251_0
# Benchmark: hotpotqa
# Data Indices: [3635, 2687, 2794, 3395, 311]

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
        It first generates an initial answer, then uses flexible custom to trace multi-hop connections step-by-step,
        and finally ensembles the results to improve accuracy.
        """
        # Step 1: Generate initial answer directly
        initial_answer = await self.answer_generate()

        # Step 2: Use FlexibleCustom in sequential mode to trace multi-hop reasoning
        # This breaks down the problem into steps like identifying key entities, finding connections, etc.
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each connection sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Review the initial answer using the multi-hop solution as context
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble the original answer and the reviewed answer to get a robust final output
        ensemble_result = await self.sc_ensemble(solutions=[initial_answer, reviewed_answer, multi_hop_solution])

        return ensemble_result
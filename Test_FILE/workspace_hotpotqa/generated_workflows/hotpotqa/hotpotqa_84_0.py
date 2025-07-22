# Workflow ID: hotpotqa_84_0
# Benchmark: hotpotqa
# Data Indices: [3325, 12, 3177, 454]

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
        It first generates an initial answer, then uses flexible custom to trace multi-hop connections,
        and finally ensembles the results for improved accuracy.
        """
        # Step 1: Generate an initial answer as a baseline
        initial_answer = await self.answer_generate()
        
        # Step 2: Use FlexibleCustom with Sequential Multi-Hop pattern to trace connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of evidence in the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )
        
        # Step 3: Review the initial answer using the multi-hop solution as context
        reviewed_answer = await self.review(pre_solution=initial_answer)
        
        # Step 4: Ensemble the initial and reviewed answers to produce a robust final output
        ensemble_solution = await self.sc_ensemble(solutions=[initial_answer, reviewed_answer, multi_hop_solution])
        
        return ensemble_solution
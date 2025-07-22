# Workflow ID: hotpotqa_813_0
# Benchmark: hotpotqa
# Data Indices: [1644, 3735, 3836, 1046]

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
        It first generates an initial answer, then refines it through review, and finally uses flexible custom reasoning
        to trace connections step-by-step across the context to ensure multi-hop accuracy.
        """
        # Step 1: Generate an initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to improve clarity and correctness
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use FlexibleCustom with Sequential Multi-Hop pattern to trace connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between facts in the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 4: Ensemble the refined answer and the multi-hop solution for robustness
        ensemble_solution = await self.sc_ensemble(solutions=[refined_answer, multi_hop_solution])

        return ensemble_solution
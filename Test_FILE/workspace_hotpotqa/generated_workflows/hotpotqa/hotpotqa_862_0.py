# Workflow ID: hotpotqa_862_0
# Benchmark: hotpotqa
# Data Indices: [1026, 1077, 36, 1264, 961]

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
        It first generates an initial answer, then refines it through iterative review and multi-hop reasoning.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to improve clarity and correctness
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use FlexibleCustom with sequential multi-hop reasoning to trace connections across context
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connecting them logically across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Ensemble the refined answer and the multi-hop solution to select the best one
        final_solution = await self.sc_ensemble(solutions=[refined_answer, multi_hop_solution])

        return final_solution
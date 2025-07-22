# Workflow ID: hotpotqa_11_0
# Benchmark: hotpotqa
# Data Indices: [2035, 714, 1972, 170]

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
        to trace connections step-by-step across multiple hops in the context.
        """
        # Step 1: Generate initial answer directly
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use FlexibleCustom with Sequential Multi-Hop pattern to trace connections
        # This ensures we break down the problem into smaller steps and reason across multiple sources
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain reasoning for each step",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Ensemble the reviewed answer and the multi-hop solution for robustness
        ensemble_solution = await self.sc_ensemble(solutions=[reviewed_answer, multi_hop_solution])

        return ensemble_solution
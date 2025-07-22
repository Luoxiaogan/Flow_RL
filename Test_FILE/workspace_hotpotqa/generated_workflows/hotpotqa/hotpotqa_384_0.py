# Workflow ID: hotpotqa_384_0
# Benchmark: hotpotqa
# Data Indices: [985, 669, 732, 3609]

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
        It breaks down the problem into steps, traces connections, and refines the answer.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and how they connect across different pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 3: Review the initial answer using the multi-hop solution as context
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble multiple solutions (initial + refined) to improve robustness
        solutions = [initial_answer, refined_answer, multi_hop_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
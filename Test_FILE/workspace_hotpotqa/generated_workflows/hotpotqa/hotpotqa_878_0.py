# Workflow ID: hotpotqa_878_0
# Benchmark: hotpotqa
# Data Indices: [3661, 2077, 659, 2832]

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
        This is a workflow graph for multi-hop question answering.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key reasoning steps
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities, connections, and reasoning steps to solve it.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        answer = await self.answer_generate()

        # Step 3: Review the generated answer using the multi-hop solution as context
        reviewed_answer = await self.review(pre_solution=answer)

        # Step 4: Ensemble multiple solutions (including original and reviewed) for robustness
        solutions = [answer, reviewed_answer, multi_hop_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
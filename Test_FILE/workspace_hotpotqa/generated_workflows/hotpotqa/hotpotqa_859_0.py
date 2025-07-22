# Workflow ID: hotpotqa_859_0
# Benchmark: hotpotqa
# Data Indices: [1587, 2162, 1845, 1551, 873]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections across multiple hops of information
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, tracing logical connections between pieces of evidence.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the final answer based on the multi-hop solution
        synthesis_instruction = "Based on the reasoning path above, provide a clear and concise answer to the question."
        final_answer = await self.custom(instruction=synthesis_instruction)

        # Step 3: Review the final answer to ensure correctness and clarity
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer
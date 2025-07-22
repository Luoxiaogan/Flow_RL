# Workflow ID: hotpotqa_90_0
# Benchmark: hotpotqa
# Data Indices: [1409, 1617, 150, 3766, 2203]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom for synthesis, followed by Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections across multiple hops
        initial_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on the reasoning path
        synthesized_answer = await self.custom(
            instruction="Based on the reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
# Workflow ID: hotpotqa_353_0
# Benchmark: hotpotqa
# Data Indices: [1459, 269, 891, 3728, 3963]

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
        It uses flexible custom for step-by-step reasoning, then synthesizes with custom,
        and finally validates with review to ensure accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = [
            "identify key entities and facts",
            "find connections between entities",
            "trace the logical path from given clues to the answer",
            "synthesize a coherent solution"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Synthesize the multi-hop reasoning into a final answer using Custom
        final_answer = await self.custom(
            instruction="Based on the multi-step reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Review the final answer for correctness and clarity
        validated_answer = await self.review(pre_solution=final_answer)

        return validated_answer
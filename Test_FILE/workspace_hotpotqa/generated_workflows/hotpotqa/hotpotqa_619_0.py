# Workflow ID: hotpotqa_619_0
# Benchmark: hotpotqa
# Data Indices: [2198, 3693, 3394, 3388, 1044]

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
        then Custom to synthesize the answer, and Review to validate it.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information.
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and connecting them logically.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to refine and synthesize the solution based on the multi-hop reasoning.
        final_answer = await self.custom(
            instruction="Based on the reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Use Review to evaluate the final answer and improve if needed.
        validated_answer = await self.review(pre_solution=final_answer)

        return validated_answer
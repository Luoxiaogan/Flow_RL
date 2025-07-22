# Workflow ID: hotpotqa_519_0
# Benchmark: hotpotqa
# Data Indices: [2624, 1659, 852, 2165]

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
        It uses flexible custom with sequential reasoning to extract and connect facts,
        then synthesizes the answer using a custom operator, and finally validates it via review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections across multiple hops
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, focusing on connecting information across different parts of the context.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the final answer based on extracted facts
        synthesis_prompt = "Based on the detailed reasoning above, generate a clear and concise final answer."
        final_answer = await self.custom(instruction=synthesis_prompt)

        # Step 3: Review the final answer for accuracy and completeness
        validated_answer = await self.review(pre_solution=final_answer)

        return validated_answer
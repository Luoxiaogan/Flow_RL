# Workflow ID: hotpotqa_806_0
# Benchmark: hotpotqa
# Data Indices: [1974, 3204, 101, 2887]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        intermediate_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and connect the information logically.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear and structured answer based on the reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a concise and accurate answer."
        )

        # Step 3: Use Review to validate the synthesized answer against the original problem
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
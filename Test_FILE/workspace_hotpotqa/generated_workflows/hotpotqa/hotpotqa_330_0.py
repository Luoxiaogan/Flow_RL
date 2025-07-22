# Workflow ID: hotpotqa_330_0
# Benchmark: hotpotqa
# Data Indices: [831, 2857, 279, 159]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_logical_path",
            "synthesize_final_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using logical reasoning.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear and structured answer from the multi-hop solution
        synthesized_answer = await self.custom(
            instruction="Based on the multi-step reasoning above, generate a concise and accurate final answer."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble multiple solutions (if needed) — here we use just one, but can be extended
        # For now, return the validated answer directly
        return validated_answer
# Workflow ID: hotpotqa_244_0
# Benchmark: hotpotqa
# Data Indices: [715, 2693, 2580, 3483, 1798]

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
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the answer with a custom operator, and finally validates it with review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between facts across different contexts
        reasoning_path = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace logical connections between facts.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the reasoned path
        synthesized_answer = await self.custom(
            instruction="Based on the detailed reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Optional: Ensemble multiple solutions if we had more than one (not used here due to single path)
        # ensemble_result = await self.sc_ensemble(solutions=[synthesized_answer, validated_answer])

        return validated_answer
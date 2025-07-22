# Workflow ID: hotpotqa_687_0
# Benchmark: hotpotqa
# Data Indices: [555, 2428, 844, 1449]

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
        # and extract relevant facts step by step
        fact_extraction = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on extracted facts
        synthesis = await self.custom(instruction="Based on the reasoning above, provide a clear and concise answer.")

        # Step 3: Use Review to validate the synthesized answer
        validated_answer = await self.review(pre_solution=synthesis)

        # Step 4: Ensemble multiple solutions (if needed) — here we just use the validated one
        # In more complex cases, you could generate multiple answers and ensemble them
        solution = validated_answer

        return solution
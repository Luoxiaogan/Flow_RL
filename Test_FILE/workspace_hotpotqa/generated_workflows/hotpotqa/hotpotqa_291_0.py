# Workflow ID: hotpotqa_291_0
# Benchmark: hotpotqa
# Data Indices: [496, 912, 1083, 1616]

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
        It uses FlexibleCustom for step-by-step reasoning to extract and connect facts,
        then Custom to synthesize the answer, followed by Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # into smaller steps like identifying entities, finding connections, etc.
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to generate a clear and structured answer based on the reasoning path
        synthesized_answer = await self.custom(instruction="Based on the reasoning steps above, generate a concise and accurate answer.")

        # Step 3: Use Review to validate the synthesized answer against the original problem
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Optional: Ensemble multiple solutions if we want to improve robustness
        # Here we use only one solution but can be expanded if needed
        final_answer = validated_answer

        return final_answer
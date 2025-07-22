# Workflow ID: hotpotqa_282_0
# Benchmark: hotpotqa
# Data Indices: [3357, 1600, 1016, 1541, 208]

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
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the reasoning path
        synthesized_answer = await self.custom(instruction="Based on the step-by-step reasoning, generate a clear and concise final answer.")

        # Step 3: Review the synthesized answer to validate its correctness
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble (optional) if multiple solutions were generated — but only one here
        # Since we have just one solution, we return it directly
        return reviewed_answer
# Workflow ID: hotpotqa_559_0
# Benchmark: hotpotqa
# Data Indices: [2550, 2692, 2638, 2313]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        Uses flexible custom for step-by-step reasoning, then synthesizes with custom, and validates with review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        reasoning_path = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps to solve it.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the solution based on the structured reasoning path
        synthesized_solution = await self.custom(
            instruction="Based on the step-by-step breakdown, generate a coherent and accurate answer."
        )

        # Step 3: Review the synthesized solution for correctness and clarity
        final_solution = await self.review(pre_solution=synthesized_solution)

        return final_solution
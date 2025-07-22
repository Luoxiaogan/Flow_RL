# Workflow ID: hotpotqa_704_0
# Benchmark: hotpotqa
# Data Indices: [464, 3072, 590, 376]

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
        It uses FlexibleCustom for structured step-by-step reasoning, 
        Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear answer based on the structured reasoning
        synthesized_solution = await self.custom(
            instruction="Based on the reasoning above, generate a concise and accurate final answer."
        )

        # Step 3: Use Review to validate and refine the synthesized solution
        final_solution = await self.review(pre_solution=synthesized_solution)

        return final_solution
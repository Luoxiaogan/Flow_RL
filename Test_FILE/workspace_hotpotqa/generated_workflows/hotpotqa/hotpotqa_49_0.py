# Workflow ID: hotpotqa_49_0
# Benchmark: hotpotqa
# Data Indices: [1987, 3811, 567, 1971]

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
        It uses FlexibleCustom for step-by-step reasoning, Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into smaller steps
        reasoning_steps = [
            "Identify key entities in the question",
            "Extract relevant facts from the context",
            "Trace connections between entities across multiple hops",
            "Synthesize the final answer based on logical inference"
        ]
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each logically.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear and structured answer based on the reasoned solution
        synthesized_answer = await self.custom(
            instruction="Based on the reasoning above, generate a concise and well-structured answer that directly addresses the question."
        )

        # Step 3: Use Review to validate the synthesized answer and refine if necessary
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
# Workflow ID: hotpotqa_403_0
# Benchmark: hotpotqa
# Data Indices: [2903, 1698, 2771, 3011, 1668]

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
        It uses flexible custom for structured multi-hop reasoning, then synthesizes with custom, and validates with review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using sequential reasoning to identify key facts and connections.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Use Custom to synthesize the solution from the multi-hop breakdown
        synthesized_solution = await self.custom(
            instruction="Based on the multi-hop reasoning above, generate a clear and concise answer with logical justification."
        )

        # Step 3: Use Review to validate and refine the synthesized solution
        final_solution = await self.review(pre_solution=synthesized_solution)

        return final_solution
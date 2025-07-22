# Workflow ID: hotpotqa_46_0
# Benchmark: hotpotqa
# Data Indices: [2232, 2702, 2843, 160]

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
        Uses FlexibleCustom (sequential reasoning) to extract and connect facts,
        then Custom to synthesize the answer, and Review to validate it.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections across multiple pieces of context
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "connect_information_across_contexts",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace connections between facts.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to generate a final answer based on the structured reasoning
        final_answer = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a clear and concise answer."
        )

        # Step 3: Review the final answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer
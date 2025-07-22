# Workflow ID: hotpotqa_12_0
# Benchmark: hotpotqa
# Data Indices: [972, 507, 935, 799]

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
        then Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "find_connections_between_entities",
            "trace_reasoning_path_to_answer"
        ]
        intermediate_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, focusing on identifying key entities and connecting them logically.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a coherent answer from the intermediate solution
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning above, synthesize a clear and concise answer to the original question."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
# Workflow ID: hotpotqa_276_0
# Benchmark: hotpotqa
# Data Indices: [3228, 79, 3682, 2946, 278]

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
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context step by step",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear and structured answer from the multi-hop solution
        synthesized_answer = await self.custom(
            instruction="Break down the solution into logical steps and explain the reasoning behind each step."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer
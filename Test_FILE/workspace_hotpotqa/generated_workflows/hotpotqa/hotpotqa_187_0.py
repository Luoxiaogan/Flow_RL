# Workflow ID: hotpotqa_187_0
# Benchmark: hotpotqa
# Data Indices: [2414, 1970, 2538, 3489]

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
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the solution with Custom, and finally validates it with Review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between facts in the context
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        initial_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and connect the information logically.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the final answer from the structured reasoning
        synthesis = await self.custom(
            instruction="Based on the logical reasoning above, provide a clear and concise answer to the question."
        )

        # Step 3: Use Review to validate the synthesized answer
        validated_answer = await self.review(pre_solution=synthesis)

        return validated_answer
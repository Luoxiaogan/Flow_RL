# Workflow ID: hotpotqa_199_0
# Benchmark: hotpotqa
# Data Indices: [125, 1085, 525, 290, 2927]

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
        then synthesizes the answer with a custom operator, and finally reviews the solution.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "find_intermediate_connections",
            "synthesize_final_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identify key entities, and trace how they connect across multiple hops.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the final answer from the multi-hop reasoning
        synthesis_instruction = "Based on the step-by-step reasoning above, generate a clear and concise final answer that directly addresses the question."
        final_answer = await self.custom(instruction=synthesis_instruction)

        # Step 3: Review the synthesized answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer
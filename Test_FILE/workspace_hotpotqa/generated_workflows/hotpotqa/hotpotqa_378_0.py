# Workflow ID: hotpotqa_378_0
# Benchmark: hotpotqa
# Data Indices: [2118, 3053, 1463, 1792, 3151]

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
        then synthesizes the answer with a custom agent, and finally reviews it for accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information
        reasoning_path = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and how they relate across multiple steps.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear and structured answer based on the traced path
        synthesis = await self.custom(
            instruction="Based on the reasoning path, generate a concise and accurate answer. Explain each step clearly."
        )

        # Step 3: Review the synthesized answer to improve clarity and correctness
        final_answer = await self.review(pre_solution=synthesis)

        return final_answer
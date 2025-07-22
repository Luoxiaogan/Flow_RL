# Workflow ID: hotpotqa_424_0
# Benchmark: hotpotqa
# Data Indices: [531, 169, 1021, 280, 274]

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
        # and trace connections across multiple pieces of information
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and their relationships to solve this multi-hop question.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning
        synthesis = await self.custom(
            instruction="Based on the reasoning above, generate a clear and concise final answer to the question."
        )

        # Step 3: Review the synthesized answer for accuracy and completeness
        reviewed_answer = await self.review(pre_solution=synthesis)

        return reviewed_answer
# Workflow ID: hotpotqa_207_0
# Benchmark: hotpotqa
# Data Indices: [1860, 2743, 979, 1513]

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
        then synthesizes the answer with a custom operator, and finally reviews it for accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear and structured answer based on the extracted facts
        synthesized = await self.custom(instruction="Based on the previous reasoning, write a clear and concise answer that connects all relevant information logically.")

        # Step 3: Use Review to validate and refine the synthesized answer
        final_answer = await self.review(pre_solution=synthesized)

        return final_answer
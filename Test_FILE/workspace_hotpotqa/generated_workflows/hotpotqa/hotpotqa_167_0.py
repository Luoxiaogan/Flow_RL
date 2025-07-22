# Workflow ID: hotpotqa_167_0
# Benchmark: hotpotqa
# Data Indices: [209, 3971, 167, 1483]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, focusing on identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a detailed answer based on the structured reasoning
        synthesis = await self.custom(
            instruction="Based on the step-by-step breakdown, generate a clear and concise answer with reasoning for each step."
        )

        # Step 3: Review the synthesized answer for accuracy and completeness
        reviewed_answer = await self.review(pre_solution=synthesis)

        # Step 4: Generate a final answer directly (as a baseline or fallback)
        direct_answer = await self.answer_generate()

        # Step 5: Ensemble the reviewed answer and direct answer to select the best one
        final_solution = await self.sc_ensemble(solutions=[reviewed_answer, direct_answer])

        return final_solution
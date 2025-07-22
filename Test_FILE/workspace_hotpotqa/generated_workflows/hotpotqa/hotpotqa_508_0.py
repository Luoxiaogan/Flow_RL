# Workflow ID: hotpotqa_508_0
# Benchmark: hotpotqa
# Data Indices: [616, 3957, 2234, 1628]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer with validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        reasoning_path = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning path
        synthesis = await self.custom(
            instruction="Based on the structured reasoning path, generate a clear and concise answer that explains how each step connects to the final solution."
        )

        # Step 3: Review the synthesized answer for accuracy and clarity
        reviewed_answer = await self.review(pre_solution=synthesis)

        # Optional: Generate an alternative answer using AnswerGenerate for ensemble (to handle uncertainty)
        alt_answer = await self.answer_generate()

        # Step 4: Ensemble the main answer and alternative to select the best one
        final_answer = await self.sc_ensemble(solutions=[reviewed_answer, alt_answer])

        return final_answer
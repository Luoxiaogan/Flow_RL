# Workflow ID: hotpotqa_834_0
# Benchmark: hotpotqa
# Data Indices: [3938, 2906, 225, 2989]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and extract intermediate facts or connections needed for multi-hop reasoning
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and relationships that connect different pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear and structured answer based on the reasoning path
        synthesis_solution = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a clear and concise answer to the original question. Make sure to explain how each piece of evidence connects to the final answer."
        )

        # Step 3: Use Review to validate the synthesized solution against the original problem context
        reviewed_solution = await self.review(pre_solution=synthesis_solution)

        # Step 4: Optionally ensemble with a direct answer (as a fallback or validation check)
        direct_answer = await self.answer_generate()
        solutions = [reviewed_solution, direct_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
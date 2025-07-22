# Workflow ID: hotpotqa_837_0
# Benchmark: hotpotqa
# Data Indices: [2222, 191, 742, 3219]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and extract intermediate facts across multiple hops
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a detailed answer based on extracted facts
        synthesized_answer = await self.custom(
            instruction="Based on the reasoning path above, generate a clear and concise answer that directly addresses the question."
        )

        # Step 3: Review the synthesized answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Generate a direct answer as a baseline for ensemble
        direct_answer = await self.answer_generate()

        # Step 5: Ensemble both answers to select the best solution
        final_solution = await self.sc_ensemble(solutions=[reviewed_answer, direct_answer])

        return final_solution
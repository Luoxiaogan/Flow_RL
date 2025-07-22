# Workflow ID: hotpotqa_463_0
# Benchmark: hotpotqa
# Data Indices: [3060, 3598, 3369, 407, 405]

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
        then synthesizes the solution with a custom agent, and finally reviews it for accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key facts and how they connect across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_facts", "find_intermediate_connections", "trace_logical_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer from the structured reasoning
        synthesis = await self.custom(
            instruction="Based on the logical path traced above, generate a clear and concise answer that directly addresses the question."
        )

        # Step 3: Review the synthesized answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=synthesis)

        # Step 4: Optionally, generate an alternative solution using direct generation for ensemble
        direct_answer = await self.answer_generate()

        # Step 5: Ensemble the two solutions to select the best one
        final_solution = await self.sc_ensemble(solutions=[reviewed_answer, direct_answer])

        return final_solution
# Workflow ID: hotpotqa_259_0
# Benchmark: hotpotqa
# Data Indices: [2548, 1454, 3392, 3696, 3698]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        """
        # Step 1: Use FlexibleCustom to perform sequential multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information in the context step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        answer = await self.answer_generate()

        # Step 3: Review the generated answer for consistency and correctness
        reviewed_answer = await self.review(pre_solution=answer)

        # Step 4: Ensemble with the flexible custom result to improve robustness
        solutions = [solution, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
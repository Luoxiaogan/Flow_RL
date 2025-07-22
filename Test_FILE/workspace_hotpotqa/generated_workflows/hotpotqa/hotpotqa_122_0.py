# Workflow ID: hotpotqa_122_0
# Benchmark: hotpotqa
# Data Indices: [3597, 2706, 2385, 2474]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to trace connections step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each connection sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning path
        answer = await self.answer_generate()

        # Step 3: Review the generated answer for correctness and clarity
        reviewed_answer = await self.review(pre_solution=answer)

        # Step 4: Ensemble with original flexible custom solution for robustness
        solutions = [solution, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer
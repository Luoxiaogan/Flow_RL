# Workflow ID: hotpotqa_631_0
# Benchmark: hotpotqa
# Data Indices: [31, 1603, 3654, 1117, 1379]

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
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning path
        final_answer = await self.answer_generate()

        # Step 3: Review the generated answer to refine it
        refined_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble with the flexible custom solution to improve accuracy
        solutions = [refined_answer, solution]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        return ensembled_answer
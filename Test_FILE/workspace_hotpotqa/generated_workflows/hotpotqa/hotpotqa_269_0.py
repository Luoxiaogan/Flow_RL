# Workflow ID: hotpotqa_269_0
# Benchmark: hotpotqa
# Data Indices: [182, 3792, 2541, 3029]

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
        It first breaks down the problem, then traces connections step-by-step, and finally refines the answer.
        """
        # Step 1: Use flexible custom to perform sequential multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information in a logical sequence.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Review the generated solution for consistency and correctness
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate an alternative answer directly (for ensemble)
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the two solutions to select the best one
        final_answer = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return final_answer
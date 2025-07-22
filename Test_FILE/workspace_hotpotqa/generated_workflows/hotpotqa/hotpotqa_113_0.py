# Workflow ID: hotpotqa_113_0
# Benchmark: hotpotqa
# Data Indices: [313, 686, 1747, 3281]

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
        It uses FlexibleCustom for structured reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to extract entities and trace connections in a sequential manner
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and their relationships step by step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        solution_2 = await self.answer_generate()

        # Step 3: Review the direct answer using the flexible custom output as context
        review_prompt = f"Review this answer: '{solution_2}' using the following reasoning path: {solution_1}"
        solution_3 = await self.review(pre_solution=review_prompt)

        # Step 4: Ensemble the three solutions to get the most reliable one
        ensemble_input = [solution_1, solution_2, solution_3]
        final_answer = await self.sc_ensemble(solutions=ensemble_input)

        return final_answer
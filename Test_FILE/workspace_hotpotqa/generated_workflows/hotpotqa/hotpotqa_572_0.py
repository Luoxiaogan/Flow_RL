# Workflow ID: hotpotqa_572_0
# Benchmark: hotpotqa
# Data Indices: [1605, 3419, 2971, 2187]

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
        This is a streamlined workflow graph for multi-hop question answering.
        It uses FlexibleCustom for structured reasoning and ensembles multiple solutions.
        """
        # Step 1: Use FlexibleCustom to extract entities and find connections in a structured way
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem by first extracting key entities, then identifying connections between them, and finally synthesizing an answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        solution2 = await self.answer_generate()

        # Step 3: Review the first solution to refine it
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions (original and reviewed) to get a robust answer
        final_solution = await self.sc_ensemble(solutions=[solution2, reviewed_solution])

        return final_solution
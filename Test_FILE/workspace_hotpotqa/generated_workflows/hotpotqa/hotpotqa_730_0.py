# Workflow ID: hotpotqa_730_0
# Benchmark: hotpotqa
# Data Indices: [2691, 2401, 1182, 248, 1522]

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
        Uses FlexibleCustom for structured reasoning and ensembles multiple solutions.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into steps: extract key entities, find connections between them, then synthesize an answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate direct answer as a baseline
        solution2 = await self.answer_generate()

        # Step 3: Review the first solution to refine it
        refined_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble all solutions to select the best one
        final_solution = await self.sc_ensemble(solutions=[solution1, solution2, refined_solution])

        return final_solution
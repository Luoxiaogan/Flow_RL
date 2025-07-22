# Workflow ID: hotpotqa_107_0
# Benchmark: hotpotqa
# Data Indices: [785, 2482, 945, 1578]

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
        # Step 1: Use flexible custom to break down the problem step-by-step
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps: extract key entities, find connections between them, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly for comparison
        solution2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions to get the best result
        ensemble_result = await self.sc_ensemble(solutions=[solution1, solution2, reviewed_solution])

        return ensemble_result
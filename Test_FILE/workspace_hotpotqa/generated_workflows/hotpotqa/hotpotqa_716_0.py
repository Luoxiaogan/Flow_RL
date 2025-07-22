# Workflow ID: hotpotqa_716_0
# Benchmark: hotpotqa
# Data Indices: [505, 1561, 3256, 85, 1023]

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
        It uses FlexibleCustom for structured reasoning and ensembles multiple solutions for robustness.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities, find connections between them, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an independent direct answer for ensemble
        solution2 = await self.answer_generate()

        # Step 3: Review the first solution to refine it
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions (original and reviewed) to get the best one
        final_answer = await self.sc_ensemble(solutions=[solution2, reviewed_solution])

        return final_answer
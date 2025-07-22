# Workflow ID: hotpotqa_681_0
# Benchmark: hotpotqa
# Data Indices: [1719, 15, 2932, 1030]

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
        It uses FlexibleCustom for structured reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps: extract entities, find connections, and synthesize the answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Review the flexible custom solution to refine it
        refined_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the direct answer and the refined solution for improved accuracy
        ensemble_result = await self.sc_ensemble(solutions=[direct_answer, refined_solution])

        return ensemble_result
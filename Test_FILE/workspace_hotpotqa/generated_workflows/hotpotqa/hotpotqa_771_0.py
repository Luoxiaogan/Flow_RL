# Workflow ID: hotpotqa_771_0
# Benchmark: hotpotqa
# Data Indices: [1656, 2336, 2120, 1917, 609]

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
        # Step 1: Use flexible custom to extract entities and find connections in a structured way
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        solution_step2 = await self.answer_generate()

        # Step 3: Review the generated answer to refine it using the structured insights
        refined_solution = await self.review(pre_solution=solution_step2)

        # Step 4: Ensemble multiple answers (including original and refined) to improve accuracy
        ensemble_input = [solution_step1, solution_step2, refined_solution]
        final_answer = await self.sc_ensemble(solutions=ensemble_input)

        return final_answer
# Workflow ID: hotpotqa_203_0
# Benchmark: hotpotqa
# Data Indices: [2269, 758, 1652, 2237, 3322]

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
        # Step 1: Use FlexibleCustom to break down the problem into key reasoning steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step by extracting entities, finding connections between them, and synthesizing an answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally refine with Review if needed (can be skipped for efficiency)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using AnswerGenerate as fallback or refinement
        final_answer = await self.answer_generate()

        # Step 4: Ensemble multiple solutions for improved accuracy (if more than one exists)
        solutions = [refined_solution, final_answer]
        ensemble_result = await self.sc_ensemble(solutions=solutions)

        return ensemble_result
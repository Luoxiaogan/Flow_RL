# Workflow ID: hotpotqa_443_0
# Benchmark: hotpotqa
# Data Indices: [2104, 1810, 836, 3628, 3571]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem,
        then ensembles multiple solutions from different reasoning paths for robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract key entities and connect them
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identify key entities, and trace logical connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an independent answer directly using AnswerGenerate
        solution2 = await self.answer_generate()

        # Step 3: Review the first solution to refine it
        refined_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions (original + refined) to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, refined_solution])

        return ensemble_solution
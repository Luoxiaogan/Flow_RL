# Workflow ID: hotpotqa_608_0
# Benchmark: hotpotqa
# Data Indices: [2204, 3458, 3928, 906]

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
        It uses flexible custom reasoning to break down the problem step-by-step,
        then refines the answer through review and ensembles multiple solutions.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities, find connections, and synthesize answer
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps: identify key entities, find relationships between them, and trace the logical path to the answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()

        # Step 3: Review the primary solution to improve accuracy
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the original solution, reviewed solution, and direct answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution, reviewed_solution, direct_answer])

        return ensemble_solution